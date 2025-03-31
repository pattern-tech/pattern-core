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
    Ensures each event is a complete JSON object with a newline terminator.
    """

    def __init__(self):
        self.queue = asyncio.Queue()

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # Create a complete JSON event for each token
        event = {"type": "token", "data": token}
        # Ensure each event ends with a newline for proper parsing
        self.queue.put_nowait(json.dumps(event) + "\n")

    def on_agent_action(self, action, **kwargs) -> None:
        event = {
            "type": "tool_start",
            "tool": getattr(action, "tool", None),
            "tool_input": getattr(action, "tool_input", {})
        }
        # Ensure each event ends with a newline for proper parsing
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

        # Use a smaller timeout to ensure more responsive streaming
        timeout = 0.01

        # Yield tokens as they become available.
        while not task.done() or not self.streaming_handler.queue.empty():
            try:
                # Get token with a short timeout to maintain streaming responsiveness
                token = await asyncio.wait_for(self.streaming_handler.queue.get(), timeout=timeout)

                # Ensure token is a complete JSON object
                if token.endswith("\n"):
                    # Token is already a complete JSON object, yield it directly
                    yield token
                else:
                    # Token might be incomplete, wait a tiny bit for more data
                    buffer = token
                    try:
                        # Try to get more data with a very short timeout
                        while not buffer.endswith("\n"):
                            more_token = await asyncio.wait_for(
                                self.streaming_handler.queue.get(),
                                timeout=0.005
                            )
                            buffer += more_token
                            # If we now have a complete line, break
                            if "\n" in buffer:
                                break
                    except asyncio.TimeoutError:
                        # If we timeout waiting for more data, that's okay
                        # We'll just yield what we have if it's complete
                        pass

                    # Process the buffer to yield complete JSON objects
                    while "\n" in buffer:
                        json_str, remaining = buffer.split("\n", 1)
                        if json_str:  # Only yield non-empty strings
                            yield json_str + "\n"
                        buffer = remaining

                    # If there's anything left in the buffer, keep it for next iteration
                    if buffer:
                        # Put it back in the queue for the next iteration
                        self.streaming_handler.queue.put_nowait(buffer)
            except asyncio.TimeoutError:
                # Short timeout to keep the loop responsive
                await asyncio.sleep(0.01)
                continue

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
