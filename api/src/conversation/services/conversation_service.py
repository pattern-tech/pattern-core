from uuid import UUID
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from langchain_core.messages.human import HumanMessage

from src.util.configuration import Config
from src.agentflow.agents.hub import AgentHub
from src.db.models import Conversation, QueryUsage
from src.agentflow.utils.shared_tools import init_llm
from src.user.services.user_service import UserService
from src.agent.services.memory_service import MemoryService
from src.project.services.project_service import ProjectService
from src.agent.services.agent_service import RouterAgentService
from src.query_usage.services.query_usage_service import QueryUsageService
from src.conversation.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Service class for handling conversation-related business logic.
    """

    def __init__(self):
        self.repository = ConversationRepository()
        self.memory_service = MemoryService()
        self.project_service = ProjectService()
        self.query_usage_service = QueryUsageService()
        self.user_service = UserService()

    def create_conversation(
        self, db_session: Session, name: str, project_id: UUID, user_id: UUID, conversation_id: UUID = None
    ) -> Conversation:
        """
        Creates a new conversation.

        Args:
            db_session (Session): The database session.
            name (str): The name of the conversation.
            project_id (UUID): The ID of the project the conversation belongs to.
            user_id (UUID): The ID of the user creating the conversation.
            conversation_id (UUID): The ID of the conversation (optional).

        Returns:
            Conversation: The created conversation instance.
        """
        conversation = Conversation(
            name=name, project_id=project_id, user_id=user_id)

        # conversation id is generated in frontend
        if conversation_id:
            conversation.id = conversation_id

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

    async def send_message(
        self,
        db_session: Session,
        message: str,
        user_id: UUID,
        conversation_id: UUID,
        message_type: str,
        stream: bool
    ):
        """
        Asynchronously processes and sends a message, either streaming the response token-by-token or returning a complete response.

        Args:
            db_session (Session): Database session for database operations
            message (str): The message to be processed
            user_id (UUID): ID of the user sending the message
            conversation_id (UUID): ID of the conversation the message belongs to
            message_type (str): Type of the message
            stream (bool): If True, streams response tokens. If False, returns complete response

        Returns:
            If stream=True:
                Generator yielding individual response tokens
            If stream=False:
                Dict containing:
                    - response (str): Complete response text
                    - intermediate_steps (List[Dict]): List of executed tool steps

        Raises:
            Exception: If associated project is not found
        """

        config = Config.get_config()

        sub_agents = AgentHub().get_agents(config["agents"])

        memory = self.memory_service.get_memory(conversation_id)

        agent = RouterAgentService(
            sub_agents=sub_agents, memory=memory, streaming=stream)

        if stream:
            try:
                # Stream tokens as they become available.
                async for token in agent.stream(message):
                    yield token
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
        else:
            result = agent.ask(message)

            intermediate_steps = []
            for step in result["intermediate_steps"]:
                intermediate_steps.append({
                    "function_name": step[0].tool,
                    "arguments": step[0].tool_input,
                    "output": step[1]
                })

            yield {
                "response": result["output"],
                "intermediate_steps": intermediate_steps
            }

        query_usage = QueryUsage(
            user_id=user_id,
            provider="morpheus",
        )
        self.query_usage_service.create_query_usage(
            db_session, query_usage)

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

    def rename_title(self, db_session: Session, conversation_id: UUID, user_id: UUID, message: str) -> str:
        config = Config.get_config()
        self.llm = init_llm(service=config["llm"]["provider"],
                            model_name=config["llm"]["model"],
                            api_key=config["llm"]["api_key"],
                            stream=False,
                            callbacks=None)
        messages = [
            (
                "system",
                "You should generate a title (maximum 5 words) for this message",
            ),
            ("human", f"{message}"),
        ]

        title = self.llm.invoke(messages)

        self.repository.update(db_session, conversation_id, {
                               "name": title.content}, user_id)

        return title.content
