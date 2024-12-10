import os
import uuid
import psycopg

from threading import Lock
from langchain_postgres import PostgresChatMessageHistory


class MemoryService:
    """
    Singleton class for managing a PostgreSQL database connection.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls,):

        _POSTGRES_DB = os.getenv("POSTGRES_DB")
        _POSTGRES_HOST = os.getenv("POSTGRES_HOST")
        _POSTGRES_PORT = os.getenv("POSTGRES_PORT")
        _POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
        _POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")

        connection_string = f"postgresql://{_POSTGRES_USERNAME}:{_POSTGRES_PASSWORD}@{_POSTGRES_HOST}:{_POSTGRES_PORT}/{_POSTGRES_DB}"

        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MemoryService, cls).__new__(cls)
                    cls._instance.connection_string = connection_string
                    cls._instance.connection = psycopg.connect(
                        connection_string)

        PostgresChatMessageHistory.create_tables(
            cls._instance.connection, "chat_history")
        return cls._instance

    def __init__(self):
        # This is called each time an instance is created, but connection is already managed.
        pass

    def get_connection(self):
        """
        Returns the existing database connection.
        """
        return self.connection

    def create_new_memory(self, table_name="chat_history"):
        """
        Creates a new memory instance in the specified table.

        Args:
            table_name (str): The name of the database table to use. Defaults to "chat_history".

        Returns:
            tuple: A tuple containing:
                - session_id (str): Unique identifier for the chat session
                - memory (PostgresChatMessageHistory): A new memory instance
        """
        session_id = uuid.uuid4()

        memory = PostgresChatMessageHistory(
            table_name,
            str(session_id),
            sync_connection=self.get_connection()
        )
        return (session_id, memory)

    def get_memory(self, session_id, table_name="chat_history"):
        """
        Retrieves an existing memory instance for a given session ID.

        Args:
            session_id (str): The unique identifier for the chat session
            table_name (str): The name of the database table to use. Defaults to "chat_history"

        Returns:
            PostgresChatMessageHistory: The memory instance associated with the session ID
        """
        memory = PostgresChatMessageHistory(
            table_name,
            str(session_id),
            sync_connection=self.get_connection()
        )
        return memory
