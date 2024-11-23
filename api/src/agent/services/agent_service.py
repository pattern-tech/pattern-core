from typing import List
from pydantic import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.agent.enum.agent_action_enum import AgentActionEnum

from dotenv import load_dotenv


load_dotenv()


class PlanStep(BaseModel):
    """Represents a single step with an action."""

    task: str = Field(description="Task definition")
    action: str = Field(description="The action to take for this step.")
    action_description: str = Field(
        description="Specify what data needs to be obtained from the user, if any, to complete the step. If no user input is required, left blank."
    )


class Plan(BaseModel):
    """Plan to follow in the future."""

    steps: List[PlanStep] = Field(
        description="Different steps to follow, should be in sorted order"
    )


class AgentService:
    def __init__(self):
        pass

    def planner(self, task: str):
        planner_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""For the given objective, come up with a simple step by step plan.
                    This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps.
                    The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.
                    
                    Step Action Guidelines
                    The step_action must be one of the following values:
                    {AgentActionEnum.NO_ACTION.value}: No additional input is required from the user to perform the step.
                    {AgentActionEnum.INPUT_TEXT.value}: Text input is required from the user to complete the step. (Based on real-wold use cases)
                    {AgentActionEnum.INPUT_MEDIA.value}: Media input (e.g., images, videos, or files) is required from the user to complete the step. (Based on real-wold use cases)
                    """,
                ),
                ("placeholder", "{messages}"),
            ]
        )

        planner = planner_prompt | ChatOpenAI(
            model="gpt-4o-mini", temperature=0
        ).with_structured_output(Plan)
        return planner
