import json
import asyncio

from langchain.agents import AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.util.configuration import Config
from src.agentflow.utils.enum import AgentType
from src.agentflow.utils.shared_tools import init_llm, init_agent, init_prompt


class StreamingCallbackHandler(BaseCallbackHandler):
    """
    A callback handler that collects tokens and intermediate events in an asyncio queue.
    Uses a newline-delimited JSON protocol.
    """

    def __init__(self):
        self.queue = asyncio.Queue()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        event = {"type": "token", "data": token}
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_agent_action(self, action, **kwargs) -> None:
        event = {
            "type": "tool_start",
            "tool": getattr(action, "tool", None),
            "tool_input": getattr(action, "tool_input", {})
        }
        self.queue.put_nowait(json.dumps(event) + "\n")


class RouterAgentService:
    """
    RouterAgentService is responsible for routing the input message to the appropriate agent
    and returning the response.
    """

    def __init__(self, sub_agents, memory=None, streaming: bool = True):
        self.sub_agents = sub_agents
        self.memory = memory
        self.streaming = streaming

        # Set up the streaming callback if streaming is enabled.
        if streaming:
            self.streaming_handler = StreamingCallbackHandler()

        config = Config.get_config()

        self.llm = init_llm(service=config["llm"]["provider"],
                            model_name=config["llm"]["model"],
                            api_key=config["llm"]["api_key"],
                            stream=streaming,
                            callbacks=[self.streaming_handler] if self.streaming else None)

        self.prompt = init_prompt(self.llm, AgentType.ROUTER_AGENT)

        self.agent = init_agent(self.llm, self.sub_agents, self.prompt)

        if streaming:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.sub_agents,
                return_intermediate_steps=True,
                verbose=True,
                callbacks=[self.streaming_handler]
            )
        else:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.sub_agents,
                return_intermediate_steps=True,
                verbose=True
            )

        if self.memory:
            self.agent_with_chat_history = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: memory,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

    async def stream(self, message: str):
        """
        Args:
            message (str): The input message to be processed by the agent.

        Yields:
            str: Tokens of the agent's response as they become available.

        Raises:
            asyncio.TimeoutError: If waiting for a token from the queue times out.

        Notes:
            - If memory is enabled, the agent's response is invoked synchronously using `run_in_executor`.
            - If memory is not enabled, the agent's response is invoked asynchronously using `arun`.
            - The method clears any leftover tokens in the queue before starting to stream the response.
            - Uses a buffer to ensure complete JSON objects are sent to prevent parsing errors.
        """
        # Clear any leftover tokens.
        while not self.streaming_handler.queue.empty():
            self.streaming_handler.queue.get_nowait()

        # If memory is enabled, use the synchronous `invoke` wrapped in run_in_executor.
        if self.memory:
            loop = asyncio.get_running_loop()
            task = loop.run_in_executor(
                None,
                lambda: self.agent_with_chat_history.invoke(
                    input={"input": message},
                    config={"configurable": {"session_id": "ـ"}}
                )
            )
        else:
            task = asyncio.create_task(
                self.agent_executor.arun({"input": message})
            )

        # Buffer to collect tokens
        buffer = ""

        # Yield tokens as they become available.
        while not task.done() or not self.streaming_handler.queue.empty():
            try:
                token = await asyncio.wait_for(self.streaming_handler.queue.get(), timeout=0.1)
                # Add token to buffer
                buffer += token

                # Check if buffer contains complete JSON objects (ending with newline)
                while "\n" in buffer:
                    # Split at the first newline
                    json_str, buffer = buffer.split("\n", 1)
                    # Only yield complete JSON objects
                    if json_str:
                        yield json_str + "\n"

            except asyncio.TimeoutError:
                continue

        # Yield any remaining complete JSON in the buffer
        if buffer and "\n" in buffer:
            parts = buffer.split("\n")
            for i in range(len(parts) - 1):
                if parts[i]:
                    yield parts[i] + "\n"

        result = await task

    def ask(self, message: str):
        """
        Sends a message to the agent and returns the response.

        Args:
            message (str): The message to send to the agent.

        Returns:
            The response from the agent.

        If the agent has memory, it uses the agent with chat history to invoke the response.
        Otherwise, it uses the agent executor to invoke the response.
        """
        if self.memory:
            return self.agent_with_chat_history.invoke(
                input={"input": message},
                config={"configurable": {"session_id": "ـ"}})
        else:
            return self.agent_executor.invoke({"input": message})
