from typing import List
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()


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
