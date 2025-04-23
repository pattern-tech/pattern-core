import json

from uuid import UUID
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from langchain_core.messages.human import HumanMessage

from src.share.logging import Logging
from src.util.configuration import Config
from src.util.exceptions import NotFoundError
from src.db.models import Conversation, QueryUsage
from src.agentflow.utils.shared_tools import init_llm
from src.user.services.user_service import UserService
from src.agentflow.MCR.dri_selection import DRISelector
from src.agentflow.MCR.mcr import retrieve_data, get_dri
from src.agent.services.agent_service import AgentService
from src.agent.services.memory_service import MemoryService
from src.project.services.project_service import ProjectService
from src.project.repositories.project_repository import ProjectRepository
from src.query_usage.services.query_usage_service import QueryUsageService
from src.conversation.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Service class for handling conversation-related business logic.
    """

    def __init__(self):
        self.user_service = UserService()
        self.memory_service = MemoryService()
        self.project_service = ProjectService()
        self.repository = ConversationRepository()
        self.project_repository = ProjectRepository()
        self.query_usage_service = QueryUsageService()

        self._logger = Logging().get_logger()

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
        if name.strip() == "":
            self._logger.error(
                f"Failed to create conversation: Name is empty. User: {user_id}")
            raise Exception("Name is required")

        if not self.project_repository.get_by_id(db_session, project_id, user_id):
            self._logger.error(
                f"Failed to create conversation: Project not exists or not owned by user. User: {user_id}, Project: {project_id}")
            raise NotFoundError("Project not exists or not owned by user")

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
            raise NotFoundError("Conversation not found")

        return conversation, messages

    def get_all_conversations(self, db_session: Session, project_id: UUID, user_id: UUID) -> List[Conversation]:
        """
        Lists all conversations for a specific project.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to retrieve conversations for.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            List[Conversation]: A list of Conversation instances.
        """
        if not self.project_service.get_project(db_session, project_id, user_id):
            raise NotFoundError("Project not exists or not owned by user")

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
        if data["name"].strip() == "":
            raise Exception("Name is required")

        if not self.project_repository.get_by_id(db_session, data["project_id"], user_id):
            raise NotFoundError("Project not exists or not owned by user")

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
        project_id: UUID,
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
            project_id (UUID): ID of the project associated with the conversation
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
        self._logger.info(
            f"Processing message for user {user_id}, conversation {conversation_id}, project {project_id}")
        self._logger.debug(
            f"Message type: {message_type}, Streaming: {stream}")

        conversation = self.repository.get_by_id(
            db_session, conversation_id, user_id)

        if not conversation:
            self._logger.error(
                f"Conversation not found: {conversation_id}, user: {user_id}")
            raise NotFoundError(
                "Conversation not found or is not owned by user")

        if conversation.project_id != project_id:
            self._logger.error(
                f"Project mismatch: expected {conversation.project_id}, got {project_id}")
            raise NotFoundError("Project not found or is not owned by user")

        chat_history = self.get_history(
            db_session, user_id, conversation_id)
        chat_history.append(message)
        self._logger.debug(
            f"Conversation {conversation_id}: Chat history retrieved, message appended")

        instruction_selection_start_event = {
            "type": "instruction_selection_start",
            "timestamp": str(datetime.now())
        }
        yield json.dumps(instruction_selection_start_event) + "\n"

        # ---------- v2.1.0 ----------

        status, selection_message = DRISelector().select_DRI(chat_history)

        self._logger.info(
            f"DRI selection for conversation {conversation_id}: status={status}")

        if status == "selected_DRI":
            self._logger.info(
                f"Selected DRIs for conversation {conversation_id}: {selection_message}")
            selected_instructions = selection_message

        instruction_selection_end_event = {
            "type": "instruction_selection_end",
            "instructions": selected_instructions,
            "timestamp": str(datetime.now())
        }
        yield json.dumps(instruction_selection_end_event) + "\n"

        selected_DRIs = []
        for dri_id in selected_instructions:
            selected_DRIs.append(get_dri(dri_id))

        self._logger.info(
            f"Retrieved {len(selected_DRIs)} DRIs for conversation {conversation_id}")

        memory = self.memory_service.get_memory(conversation_id)

        self._logger.info(
            f"Creating agent for conversation {conversation_id}, streaming={stream}")
        agent = AgentService(
            tools=[retrieve_data], MCR=selected_DRIs, memory=memory, streaming=stream)

        if stream:
            try:
                self._logger.info(
                    f"Starting streaming for conversation {conversation_id}")
                # Stream tokens as they become available.
                token_count = 0
                async for token in agent.stream(message):
                    token_count += 1
                    if token_count % 50 == 0:  # Log every 50 tokens to avoid excessive logging
                        self._logger.debug(
                            f"Streamed {token_count} tokens for conversation {conversation_id}")
                    yield token
                self._logger.info(
                    f"Streaming completed for conversation {conversation_id}, total tokens: {token_count}")
            except Exception as e:
                self._logger.error(
                    f"Error during streaming for conversation {conversation_id}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                )
        else:
            self._logger.info(
                f"Requesting non-streaming response for conversation {conversation_id}")
            result = agent.ask(message)

            self._logger.info(
                f"Response received for conversation {conversation_id}, length: {len(result.get('output', ''))}")
            self._logger.debug(
                f"Intermediate steps: {len(result.get('intermediate_steps', []))}")

            intermediate_steps = []
            for step in result["intermediate_steps"]:
                intermediate_steps.append({
                    "function_name": step[0].tool,
                    "arguments": step[0].tool_input,
                    "output": step[1]
                })
                self._logger.debug(f"Tool used: {step[0].tool}")

            yield {
                "response": result["output"],
                "intermediate_steps": intermediate_steps
            }

        self._logger.info(f"Recording query usage for user {user_id}")
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
        generated_id = 0
        for message in memory.messages:
            history.append({
                "id": generated_id,
                "role": "human" if isinstance(message, HumanMessage) else "ai",
                "content": message.content,
            })
            generated_id += 1
        return history

    def get_user_messages(self, conversation_id: UUID):
        """
        Retrieves only the user (human) messages from a conversation.

        Args:
            conversation_id (UUID): ID of the conversation to get messages from

        Returns:
            list: List of HumanMessage objects from the conversation
        """
        memory = self.memory_service.get_memory(conversation_id)
        # filter user messages
        user_messages = [
            message.content for message in memory.messages if isinstance(message, HumanMessage)]
        return user_messages

    def rename_title(self, db_session: Session, conversation_id: UUID, user_id: UUID, message: str) -> str:
        """
        Renames a conversation title using the LLM to generate a title.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to rename.
            user_id (UUID): The ID of the user renaming the conversation.
            message (str): The message to generate a title for.

        Returns:
            str: The new title of the conversation.
        """
        self._logger.info(
            f"Generating title for conversation {conversation_id}, user {user_id}")

        config = Config.get_config()
        self._logger.debug(
            f"Using LLM provider: {config['llm']['provider']}, model: {config['llm']['model']}")

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

        self._logger.debug(
            f"Sending title generation request to LLM for conversation {conversation_id}")
        title = self.llm.invoke(messages)
        self._logger.info(
            f"Title generated for conversation {conversation_id}: '{title.content}'")

        self.repository.update(db_session, conversation_id, {
                               "name": title.content}, user_id)

        return title.content
