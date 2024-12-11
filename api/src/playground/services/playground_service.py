from uuid import UUID
from typing import Set
from typing import List
from sqlalchemy.orm import Session
from langchain_core.messages.human import HumanMessage

from src.agent.services.memory_service import MemoryService
from src.project.services.project_service import ProjectService
from src.agent.services.agent_service import DataProviderAgentService
from src.agent.tools.tools_index import tool_function_index


class PlayGroundService:
    """
    Service class for handling sending message to playground
    """

    def __init__(self):
        self.memory_service = MemoryService()
        self.project_service = ProjectService()

    def send_message(
        self,
        db_session: Session,
        message: str,
        user_id: UUID,
        conversation_id: UUID,
        project_id: UUID,
        message_type: str
    ):
        """
        Send a message to the playground and get response from agent.

        Args:
            db_session (Session): Database session
            message (str): Message to send to agent
            user_id (UUID): ID of the user sending message
            conversation_id (UUID): ID of the conversation
            project_id (UUID): ID of the project
            message_type (str): Type of message being sent

        Returns:
            dict: Dictionary containing:
                - response (str): Output response from agent
                - intermediate_steps (list): Steps taken by agent to generate response
        """

        tools, num_tools = self.project_service.get_project_tools(
            db_session, project_id)

        tool_names = [tool["function_name"] for tool in tools]

        tools = [tool for tool in tool_function_index if tool.name in tool_names]

        memory = self.memory_service.get_memory(conversation_id)

        agent = DataProviderAgentService(tools, memory)

        result = agent.ask(message)

        return {
            "response": result["output"],
            "intermediate_steps": result["intermediate_steps"]
        }

    def get_hisotry(
        self,
        db_session: Session,
        user_id: UUID,
        conversation_id: UUID,
    ):
        """
        Get conversation history for a given conversation.

        Args:
            db_session (Session): Database session
            user_id (UUID): ID of the user requesting history
            conversation_id (UUID): ID of the conversation to get history for

        Returns:
            list: List of message dictionaries containing:
                - role (str): Either "human" or "ai" indicating message sender
                - content (str): Message content
                - additional_kwargs (dict): Additional message metadata
                - response_metadata (dict): Response metadata for AI messages
        """
        memory = self.memory_service.get_memory(conversation_id)
        print(memory.messages)
        history = []
        for message in memory.messages:
            history.append({
                "role": "human" if isinstance(message, HumanMessage) else "ai",
                "content": message.content,
                "additional_kwargs": message.additional_kwargs,
                "response_metadata": message.response_metadata
            })
        return history
