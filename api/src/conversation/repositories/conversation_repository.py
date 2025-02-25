from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session

from src.db.models import Conversation
from src.share.base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """
    Repository class for handling CRUD operations on the Conversation model.
    """

    def get_by_id(self, db_session: Session, id: UUID, user_id: UUID) -> Optional[Conversation]:
        """
        Retrieves a conversation by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the conversation.
            user_id (UUID): The ID of the user who owns the conversation.

        Returns:
            Optional[Conversation]: The conversation if found, otherwise None.
        """
        return (
            db_session.query(Conversation)
            .filter(Conversation.id == id, Conversation.user_id == user_id)
            .first()
        )

    def get_all(self, db_session: Session, project_id: UUID) -> List[Conversation]:
        """
        Retrieves all conversations associated with a specific project.

        Args:
            db_session (Session): The database session to use.
            project_id (UUID): The ID of the project.

        Returns:
            List[Conversation]: A list of all conversations for the project.
        """
        return db_session.query(Conversation).filter(Conversation.project_id == project_id).all()

    def create(self, db_session: Session, conversation: Conversation) -> Conversation:
        """
        Creates a new conversation.

        Args:
            db_session (Session): The database session to use.
            conversation (Conversation): The conversation instance to add.

        Returns:
            Conversation: The created conversation instance.
        """
        db_session.add(conversation)
        db_session.commit()
        db_session.refresh(conversation)
        return conversation

    def update(self, db_session: Session, id: UUID, conversation_data: dict, user_id: UUID) -> Conversation:
        """
        Updates an existing conversation.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the conversation to update.
            conversation_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user who owns the conversation.

        Returns:
            Conversation: The updated conversation instance.

        Raises:
            Exception: If the conversation is not found.
        """
        conversation = self.get_by_id(db_session, id, user_id)
        if not conversation:
            raise Exception("Conversation not found")
        for key, value in conversation_data.items():
            setattr(conversation, key, value)
        db_session.commit()
        db_session.refresh(conversation)
        return conversation

    def delete(self, db_session: Session, id: UUID, user_id: UUID) -> None:
        """
        Deletes a conversation by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the conversation to delete.
            user_id (UUID): The ID of the user who owns the conversation.

        Raises:
            Exception: If the conversation is not found.
        """
        conversation = self.get_by_id(db_session, id, user_id)
        if not conversation:
            raise Exception("Conversation not found")

        db_session.delete(conversation)
        db_session.commit()

    def get_project_associated_with_conversation(self, db_session: Session, conversation_id: UUID) -> Optional[UUID]:
        """
        Retrieves the project ID associated with a conversation.

        Args:
            db_session (Session): The database session to use.
            conversation_id (UUID): The unique identifier of the conversation.

        Returns:
            Optional[UUID]: The project ID associated with the conversation, or None if not found.
        """
        conversation = db_session.query(Conversation).filter(
            Conversation.id == conversation_id).first()
        return conversation.project_id if conversation else None
