from uuid import UUID
from sqlalchemy import desc
from typing import Optional, List
from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.db.models import Tool
from src.share.base_repository import BaseRepository


class ToolRepository(BaseRepository[Tool]):
    """
    Repository class for handling CRUD operations on the Tool model.
    """

    def get_by_id(self, db_session: Session, id: UUID) -> Optional[Tool]:
        """
        Retrieves a tool by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the tool.

        Returns:
            Optional[Tool]: The tool if found, otherwise None.
        """
        return db_session.query(Tool).filter(Tool.id == id).first()

    def get_by_function_name(
        self, db_session: Session, function_name: str
    ) -> Optional[Tool]:
        """
        Retrieves a tool by its function_name.

        Args:
            db_session (Session): The database session to use.
            function_name (str): The unique identifier of the tool.

        Returns:
            Optional[Tool]: The tool if found, otherwise None.
        """
        return (
            db_session.query(Tool).filter(
                Tool.function_name == function_name).first()
        )

    def get_all(self, db_session: Session, limit: int, offset: int) -> List[Tool]:
        """
        Retrieves all tools.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[Tool]: A list of all tools.
        """
        return db_session.query(Tool).order_by(desc(Tool.created_at)).offset(offset).limit(limit).all()

    def get_tool_count(self, db_session: Session) -> int:
        """
        Retrieves the total count of tools.

        Args:
            db_session (Session): The database session to use.

        Returns:
            int: The total count of tools.
        """
        return db_session.query(Tool).count()

    def search_tools(
        self, db_session: Session, query: str, active: Optional[bool], limit: int, offset: int
    ):
        """
        Searches for tools based on the query and optional filters.

        Args:
            db_session (Session): The database session.
            query (str): The search keyword.
            active (Optional[bool]): Filter by active status (True/False). Default is no filter.
            limit (int): Number of items to retrieve.
            offset (int): Number of items to skip.

        Returns:
            tuple: A tuple containing the list of tools and total count.
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
        total_count = search_query.count()

        # Apply pagination
        tools = search_query.offset(offset).limit(limit).all()

        return tools, total_count

    def create(self, db_session: Session, tool: Tool) -> Tool:
        """
        Creates a new tool.

        Args:
            db_session (Session): The database session to use.
            tool (Tool): The tool instance to add.

        Returns:
            Tool: The created tool instance.
        """
        db_session.add(tool)
        db_session.commit()
        db_session.refresh(tool)
        return tool

    def update(self, db_session: Session, id: UUID, tool_data: dict) -> Tool:
        """
        Updates an existing tool.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the tool to update.
            tool_data (dict): A dictionary of fields to update.

        Returns:
            Tool: The updated tool instance.

        Raises:
            Exception: If the tool is not found.
        """
        tool = self.get_by_id(db_session, id)
        if not tool:
            raise Exception("Tool not found")
        for key, value in tool_data.items():
            setattr(tool, key, value)
        db_session.commit()
        db_session.refresh(tool)
        return tool

    def delete(self, db_session: Session, id: UUID) -> None:
        """
        Deletes a tool by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the tool to delete.

        Raises:
            Exception: If the tool is not found.
        """
        tool = self.get_by_id(db_session, id)
        if not tool:
            raise Exception("Tool not found")
        db_session.delete(tool)
        db_session.commit()
