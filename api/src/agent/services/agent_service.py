import os
import json
import asyncio

from typing import List
from langchain import hub
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import (AgentExecutor,
                              create_openai_functions_agent,
                              create_tool_calling_agent)

from src.agentflow.utils.shared_tools import init_llm, init_agent


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

        self.llm = init_llm(service=os.environ["LLM_PROVIDER"],
                            model_name=os.environ["LLM_MODEL"],
                            api_key=os.environ["LLM_API_KEY"],
                            stream=streaming,
                            callbacks=[self.streaming_handler] if self.streaming else None)

        self.prompt = hub.pull("pattern-agent/pattern-agent")
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

        # Yield tokens as they become available.
        while not task.done() or not self.streaming_handler.queue.empty():
            try:
                token = await asyncio.wait_for(self.streaming_handler.queue.get(), timeout=0.1)
                yield token
            except asyncio.TimeoutError:
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
