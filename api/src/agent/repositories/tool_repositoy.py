from uuid import UUID
from typing import Optional, List
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
            db_session.query(Tool).filter(Tool.function_name == function_name).first()
        )

    def get_all(self, db_session: Session) -> List[Tool]:
        """
        Retrieves all tools.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[Tool]: A list of all tools.
        """
        return db_session.query(Tool).all()

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
