from uuid import uuid4
from typing import Optional, List
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.tool.repositories.tool_repository import ToolRepository
from src.vectordb.services.vectordb_service import VectorDBService
from langchain_core.documents import Document
from uuid import UUID


class ToolService:
    def __init__(self):
        self.repository = ToolRepository()

    def search_tools(
        self, db_session: Session, query: str, active: bool, limit: int, offset: int
    ):
        """
        Search for tools based on query parameters.

        Args:
            db_session (Session): Database session object
            query (str): Search query string
            active (bool): Filter by active status
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip for pagination

        Returns:
            tuple: A tuple containing:
                - list: List of Tool objects matching the search criteria
                - int: Total count of matching tools before pagination
        """
        tools, total_count = self.repository.search_tools(
            db_session, query, active, limit, offset)
        return (tools, total_count)
