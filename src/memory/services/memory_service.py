import uuid
import logging

from sqlalchemy import desc
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from src.db.models import ChatHistory


class MemoryService:
    """
    Service for managing chat history in PostgreSQL database using SQLAlchemy.
    """
    _logger = logging.getLogger(__name__)

    def create_new_memory(self):
        """
        Creates a new memory session.

        Returns:
            str: Unique identifier for the chat session (session_id)
        """
        return str(uuid.uuid4())

    def add_user_message(self, db_session: Session, session_id: str, content: str, metadata=None):
        """
        Adds a user/human message to the chat history.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            content (str): The message content
            metadata (dict): Optional metadata for the message

        Returns:
            str: The ID of the created message as string
        """
        return self._add_message(db_session, session_id, "human", content, metadata)

    def add_ai_message(self, db_session: Session, session_id: str, content: str, metadata=None):
        """
        Adds an AI message to the chat history.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            content (str): The message content
            metadata (dict): Optional metadata for the message

        Returns:
            str: The ID of the created message as string
        """
        return self._add_message(db_session, session_id, "ai", content, metadata)

    def add_system_message(self, db_session: Session, session_id: str, content: str, metadata=None):
        """
        Adds a system message to the chat history.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            content (str): The message content
            metadata (dict): Optional metadata for the message

        Returns:
            str: The ID of the created message as string
        """
        return self._add_message(db_session, session_id, "system", content, metadata)

    def _add_message(self, db_session: Session, session_id: str, type: str, content: str, metadata=None):
        """
        Private method to add a message to the chat history.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            type (str): Message type ('human', 'ai', 'system', etc.)
            content (str): The message content
            metadata (dict): Optional metadata for the message

        Returns:
            str: The ID of the created message as string
        """
        try:
            message = ChatHistory(
                session_id=uuid.UUID(session_id),
                type=type,
                content=content,
                metadata=metadata
            )
            db_session.add(message)
            db_session.flush()  # Flush to get the ID without committing yet
            db_session.commit()  # Commit the transaction
            return str(message.id)
        except Exception as e:
            self._logger.error(f"Error adding message to chat history: {e}")
            raise

    def get_messages(self, db_session: Session, session_id: str, limit=None, message_type=None):
        """
        Retrieves messages for a given session ID, ordered by creation time.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            limit (int, optional): Maximum number of messages to retrieve
            message_type (str, optional): Filter by message type (human, ai, system)

        Returns:
            list: A list of dictionaries with message data
        """
        try:
            query = (
                db_session.query(ChatHistory)
                .filter(ChatHistory.session_id == uuid.UUID(session_id))
                .filter(ChatHistory.deleted_at == None)
            )

            if message_type:
                query = query.filter(ChatHistory.type == message_type)

            query = query.order_by(ChatHistory.created_at)

            if limit:
                query = query.limit(limit)

            messages = query.all()

            return [
                {
                    "id": str(msg.id),
                    "type": msg.type,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "metadata": msg.metadata
                }
                for msg in messages
            ]
        except Exception as e:
            self._logger.error(
                f"Error retrieving messages from chat history: {e}")
            return []

    def get_latest_messages(self, db_session: Session, session_id: str, limit=10):
        """
        Retrieves the most recent messages for a given session ID.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session
            limit (int): Maximum number of messages to retrieve

        Returns:
            list: A list of dictionaries with message data, newest first
        """
        try:
            messages = (
                db_session.query(ChatHistory)
                .filter(ChatHistory.session_id == uuid.UUID(session_id))
                .filter(ChatHistory.deleted_at == None)
                .order_by(desc(ChatHistory.created_at))
                .limit(limit)
                .all()
            )

            # Convert to list of dictionaries
            result = [
                {
                    "id": str(msg.id),
                    "type": msg.type,
                    "content": msg.content,
                    "created_at": msg.created_at,
                    "metadata": msg.metadata
                }
                for msg in messages
            ]

            # Reverse to get chronological order
            return result[::-1]
        except Exception as e:
            self._logger.error(f"Error retrieving latest messages: {e}")
            return []

    def clear_messages(self, db_session: Session, session_id: str):
        """
        Soft-deletes all messages for a given session ID by setting deleted_at timestamp.

        Args:
            db_session (Session): The database session to use.
            session_id (str): The unique identifier for the chat session

        Returns:
            int: Number of messages deleted
        """
        try:
            now = datetime.now(timezone.utc)
            messages = (
                db_session.query(ChatHistory)
                .filter(ChatHistory.session_id == uuid.UUID(session_id))
                .filter(ChatHistory.deleted_at == None)
                .all()
            )

            for msg in messages:
                msg.deleted_at = now

            return len(messages)
        except Exception as e:
            self._logger.error(f"Error clearing messages: {e}")
            return 0

    def delete_message(self, db_session: Session, message_id: str):
        """
        Soft-deletes a specific message by ID.

        Args:
            db_session (Session): The database session to use.
            message_id (str): The unique identifier for the message

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message = (
                db_session.query(ChatHistory)
                .filter(ChatHistory.id == uuid.UUID(message_id))
                .first()
            )

            if message:
                message.deleted_at = datetime.now(timezone.utc)
                return True
            return False
        except Exception as e:
            self._logger.error(f"Error deleting message: {e}")
            return False
