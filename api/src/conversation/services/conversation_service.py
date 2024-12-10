from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.db.models import Conversation
from src.conversation.repositories.conversation_repository import ConversationRepository


class ConversationService:
    """
    Service class for handling conversation-related business logic.
    """

    def __init__(self):
        self.repository = ConversationRepository()

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
        if not conversation:
            raise Exception("Conversation not found")
        return conversation

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
        self, db_session: Session, conversation_id: UUID, data: dict, project_id: UUID
    ) -> Conversation:
        """
        Updates a conversation with the given data.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to update.
            data (dict): A dictionary containing the fields to update.
            project_id (UUID): The ID of the project the conversation belongs to.

        Returns:
            Conversation: The updated conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        return self.repository.update(db_session, conversation_id, data, project_id)

    def delete_conversation(
        self, db_session: Session, conversation_id: UUID, project_id: UUID
    ) -> None:
        """
        Deletes a conversation.

        Args:
            db_session (Session): The database session.
            conversation_id (UUID): The ID of the conversation to delete.
            project_id (UUID): The ID of the project the conversation belongs to.

        Returns:
            None
        """
        self.repository.delete(db_session, conversation_id, project_id)
