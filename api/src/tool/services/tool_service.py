from uuid import uuid4
from typing import Optional, List
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.tool.repositories.tool_repository import ToolRepository
from src.vectordb.services.vectordb_service import VectorDBService
from src.project.repositories.project_repository import ProjectRepository
from langchain_core.documents import Document
from uuid import UUID


class ToolService:
    def __init__(self):
        self.repository = ToolRepository()
        self.project_repository = ProjectRepository()

    def get_all_tools(
        self, db_session: Session, project_id: UUID, query: str, active: bool, limit: int = None, offset: int = None
    ):
        """
        Search for tools based on query parameters.

        Args:
            db_session (Session): Database session object
            project_id (UUID): Project identifier
            query (str): Search query string
            active (bool): Filter by active status
            limit (int): Maximum number of results to return
            offset (int): Number of results to skip for pagination

        Returns:
            tuple: A tuple containing:
                - list: List of tuples, each containing a Tool object and its selection status ("selected"/"unselected")
                - int: Total count of matching tools before pagination
        """
        tools, total_count = self.repository.get_all(
            db_session, query, active, limit, offset)

        user_tools, _ = self.project_repository.get_tools_for_project(
            db_session, project_id)

        final_tools = []
        user_tools_id = [tool["id"] for tool in user_tools]
        for tool in tools:
            if tool.id in user_tools_id:
                final_tools.append({"id": tool.id,
                                    "name": tool.name,
                                    "description": tool.description,
                                    "selected": True})
            else:
                final_tools.append({"id": tool.id,
                                    "name": tool.name,
                                    "description": tool.description,
                                    "selected": False})

        return final_tools, total_count
