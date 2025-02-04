from uuid import UUID
from sqlalchemy import desc
from typing import Optional, List, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.share.base_repository import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    """
    Repository class for handling CRUD operations on the Tool model.
    """

    def get_all(
        self, db_session: Session, query: str, active: Optional[bool], limit: int = None, offset: int = None
    ) -> Tuple[List[Tool], int]:
        """
        Get all tools based on the query and optional filters.

        Args:
            db_session (Session): The database session.
            query (str): The search keyword.
            active (Optional[bool]): Filter by active status (True/False). Default is no filter.
            limit (int): Number of items to retrieve.
            offset (int): Number of items to skip.

        Returns:
            tuple: A tuple containing (list of tools, total count).
        """
        # Base query
        if (query.strip() != ""):
            search_query = db_session.query(Tool).filter(
                or_(
                    # Case-insensitive search on name
                    Tool.name.ilike(f"%{query}%"),
                    # Case-insensitive search on description
                    Tool.description.ilike(f"%{query}%")
                )
            )
        else:
            search_query = db_session.query(Tool)

        # Optional filter for active status
        if active is not None:
            search_query = search_query.filter(Tool.active == active)

        # Get total count before applying pagination
        tools_count = search_query.count()

        if limit is None or offset is None:
            tools = search_query.all()
        else:
            # Apply pagination
            tools = search_query.offset(offset).limit(limit).all()

        return (tools, tools_count)

    def get_by_id(self, db_session: Session, id: UUID) -> Optional[Tool]:
        pass

    def create(self, db_session: Session, tool: Tool) -> Tool:
        pass

    def update(self, db_session: Session, id: UUID, tool_data: dict) -> Tool:
        pass

    def delete(self, db_session: Session, id: UUID) -> None:
        pass
