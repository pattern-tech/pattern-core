import json
import asyncio

from typing import List
from langchain import hub
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.callbacks import StdOutCallbackHandler
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.agents import AgentExecutor, create_openai_functions_agent


class PlanStep(BaseModel):
    """Represents a single step with an action."""

    task: str = Field(description="Task definition")
    tools: List[str] = []
    action: str = Field(description="The action to take for this step.")


class Plan(BaseModel):
    """Plan to follow in the future."""

    steps: List[PlanStep] = Field(
        description="Different steps to follow, should be in sorted order"
    )


class SimplePlan(BaseModel):
    """Plan to follow in future"""

    steps: List[str] = Field(
        description="different steps to follow, should be in sorted order"
    )


class AgentService:
    def __init__(self):
        pass

    def planner(self, tools: list):
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    For the given objective, create a clear, step-by-step plan with the following requirements:

                    Each step should outline a specific task that contributes to achieving the final answer.
                    Avoid unnecessary or redundant steps.
                    Ensure that each step includes all necessary information to be independently actionable.
                    The result of the final step should directly provide the solution.

                    You have access to the following tools:
                    {tools}

                    Use these guidelines to decide the action for each task:

                    If the task requires a tool and the tool is available, set action to `tool_picked` and specify the tools.
                    If the task can be done without a tool, set action to `no_tool_need`.
                    If the task cannot be completed without a tool and no suitable tool is available, set action to `no_tool_found`.
                    """,
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner = planner_prompt | ChatOpenAI(
            model="gpt-4o-mini", temperature=0
        ).with_structured_output(Plan)
        return planner

    def simple_planner(self):
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """For the given objective, come up with a simple step by step plan. \
        This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
        The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.""",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner = planner_prompt | ChatOpenAI(
            model="gpt-4o-mini", temperature=0
        ).with_structured_output(SimplePlan)
        return planner


# class DataProviderAgentService:

#     def __init__(self, tools, memory=None):
#         self.tools = tools

#         self.llm = ChatOpenAI(model="gpt-4o-mini")
#         self.prompt = hub.pull("pattern-agent/pattern-agent")
#         self.agent = create_openai_functions_agent(
#             self.llm,
#             self.tools,
#             self.prompt)
#         self.agent_executor = AgentExecutor(
#             agent=self.agent,
#             tools=self.tools,
#             return_intermediate_steps=True,
#             verbose=True)

#         self.memory = memory

#         if self.memory:
#             self.agent_with_chat_history = RunnableWithMessageHistory(
#                 self.agent_executor,
#                 lambda session_id: memory,
#                 input_messages_key="input",
#                 history_messages_key="chat_history",
#             )

#     def ask(self, message):
#         if self.memory:
#             return self.agent_with_chat_history.invoke(
#                 input={"input": message},
#                 config={"configurable": {"session_id": "ـ"}})
#         else:
#             return self.agent_executor.invoke({"input": message})


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


class DataProviderAgentService:
    """
    Agent service that uses LangChain to generate responses and streams them token-by-token.
    """

    def __init__(self, tools, memory=None, streaming: bool = True):
        self.tools = tools
        self.memory = memory
        self.streaming = streaming

        # Set up the streaming callback if streaming is enabled.
        if streaming:
            self.streaming_handler = StreamingCallbackHandler()
            self.llm = ChatOpenAI(
                model="gpt-4o-mini",
                streaming=True,
                callbacks=[self.streaming_handler]
            )
        else:
            self.llm = ChatOpenAI(model="gpt-4o-mini")

        self.prompt = hub.pull("pattern-agent/pattern-agent")
        self.agent = create_openai_functions_agent(
            self.llm,
            self.tools,
            self.prompt
        )

        if streaming:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                return_intermediate_steps=True,
                verbose=True,
                callbacks=[self.streaming_handler]
            )
        else:
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
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
        Asynchronously stream the agent’s response token-by-token.
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
        if self.memory:
            return self.agent_with_chat_history.invoke(
                input={"input": message},
                config={"configurable": {"session_id": "ـ"}})
        else:
            return self.agent_executor.invoke({"input": message})
