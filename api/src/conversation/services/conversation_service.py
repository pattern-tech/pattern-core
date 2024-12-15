from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.db.models import Conversation
from langchain_core.messages.human import HumanMessage
from src.agent.tools.tools_index import tool_function_index
from src.agent.services.memory_service import MemoryService
from src.project.services.project_service import ProjectService
from src.agent.services.agent_service import DataProviderAgentService
from src.conversation.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Service class for handling conversation-related business logic.
    """

    def __init__(self):
        self.repository = ConversationRepository()
        self.memory_service = MemoryService()
        self.project_service = ProjectService()

    def create_conversation(
        self, db_session: Session, name: str, project_id: UUID, user_id: UUID
    ) -> Conversation:
        """
        Creates a new conversation.

        Args:
            db_session (Session): The database session.
            name (str): The name of the conversation.
            project_id (UUID): The ID of the project the conversation belongs to.
            user_id (UUID): The ID of the user creating the conversation.

        Returns:
            Conversation: The created conversation instance.
        """
        conversation = Conversation(
            name=name, project_id=project_id, user_id=user_id)
        return self.repository.create(db_session, conversation)

    def get_conversation(
        self, db_session: Session, conversation_id: UUID, user_id: UUID
    ) -> Conversation:
        """
        Retrieves a conversation by its ID.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to retrieve.
            project_id (UUID): The ID of the project the conversation belongs to.

        Returns:
            Conversation: The conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        conversation = self.repository.get_by_id(
            db_session, conversation_id, user_id)

        messages = self.get_history(
            db_session, user_id, conversation_id)

        if not conversation:
            raise Exception("Conversation not found")

        return conversation, messages

    def get_all_conversations(self, db_session: Session, project_id: UUID) -> List[Conversation]:
        """
        Lists all conversations for a specific project.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to retrieve conversations for.

        Returns:
            List[Conversation]: A list of Conversation instances.
        """
        return self.repository.get_all(db_session, project_id)

    def update_conversation(
        self, db_session: Session, conversation_id: UUID, data: dict, user_id: UUID
    ) -> Conversation:
        """
        Updates a conversation with the given data.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to update.
            data (dict): A dictionary containing the fields to update.
            user_id (UUID): The ID of the user updating the conversation.

        Returns:
            Conversation: The updated conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        return self.repository.update(db_session, conversation_id, data, user_id)

    def delete_conversation(
        self, db_session: Session, conversation_id: UUID, user_id: UUID
    ) -> None:
        """
        Deletes a conversation.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to delete.
            user_id (UUID): The ID of the user deleting the conversation.

        Returns:
            None
        """
        self.repository.delete(db_session, conversation_id, user_id)

    def get_project_associated_with_conversation(self, db_session: Session, conversation_id: UUID) -> UUID:
        """
        Retrieves the project ID associated with a conversation.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation.

        Returns:
            UUID: The project ID associated with the conversation.
        """
        return self.repository.get_project_associated_with_conversation(db_session, conversation_id)

    def send_message(
        self,
        db_session: Session,
        message: str,
        user_id: UUID,
        conversation_id: UUID,
        message_type: str
    ):
        """
        Send a message to the chat and get response from agent.

        Args:
            db_session (Session): Database session
            message (str): Message to send to agent
            user_id (UUID): ID of the user sending message
            conversation_id (UUID): ID of the conversation
            message_type (str): Type of message being sent

        Returns:
            dict: Dictionary containing:
                - response (str): Output response from agent
                - intermediate_steps (list): Steps taken by agent to generate response
        """

        project_id = self.get_project_associated_with_conversation(
            db_session, conversation_id)

        if project_id is None:
            raise Exception("Project not found")

        tools, num_tools = self.project_service.get_project_tools(
            db_session, project_id)

        tool_names = [tool["function_name"] for tool in tools]

        tools = [tool for tool in tool_function_index if tool.name in tool_names]

        # add default tool (get_current_datetime)
        if len(tools) == 0:
            get_current_datetime_tool = next(
                (tool for tool in tool_function_index if tool.name == "get_current_datetime"), None)
            if get_current_datetime_tool:
                tools.append(get_current_datetime_tool)

        memory = self.memory_service.get_memory(conversation_id)

        agent = DataProviderAgentService(tools, memory)

        result = agent.ask(message)

        intermediate_steps = []
        for step in result["intermediate_steps"]:
            intermediate_steps.append({
                "function_name": step[0].tool,
                "arguments": step[0].tool_input,
                "output": step[1]
            })

        return {
            "response": result["output"],
            "intermediate_steps": intermediate_steps
        }

    def get_history(
        self,
        db_session: Session,
        user_id: UUID,
        conversation_id: UUID,
    ):
        """
        Get conversation history for a given conversation.

        Args:f
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

        history = []
        for message in memory.messages:
            history.append({
                "role": "human" if isinstance(message, HumanMessage) else "ai",
                "content": message.content,
            })
        return history
