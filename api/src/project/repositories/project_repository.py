from uuid import UUID
from typing import Optional, List, Set
from sqlalchemy.orm import Session

from src.db.models import Project, Tool
from src.share.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Repository class for handling CRUD operations on the Project model.
    """

    def get_by_id(self, db_session: Session, id: UUID, user_id: UUID) -> Optional[Project]:
        """
        Retrieves a project by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the project.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            Optional[Project]: The project if found, otherwise None.
        """
        return (
            db_session.query(Project)
            .filter(Project.id == id, Project.user_id == user_id)
            .first()
        )

    def get_all(self, db_session: Session, user_id: UUID) -> List[Project]:
        """
        Retrieves all projects owned by a specific user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The ID of the user who owns the projects.

        Returns:
            List[Project]: A list of all projects for the user.
        """
        return db_session.query(Project).filter(Project.user_id == user_id).all()

    def create(self, db_session: Session, project: Project) -> Project:
        """
        Creates a new project.

        Args:
            db_session (Session): The database session to use.
            project (Project): The project instance to add.

        Returns:
            Project: The created project instance.
        """
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        return project

    def update(self, db_session: Session, id: UUID, project_data: dict, user_id: UUID) -> Project:
        """
        Updates an existing project.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the project to update.
            project_data (dict): A dictionary of fields to update.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            Project: The updated project instance.
        """
        project = self.get_by_id(db_session, id, user_id)
        if not project:
            raise Exception("Project not found")
        for key, value in project_data.items():
            setattr(project, key, value)
        db_session.commit()
        db_session.refresh(project)
        return project

    def delete(self, db_session: Session, id: UUID, user_id: UUID) -> None:
        """
        Deletes a project by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the project to delete.
            user_id (UUID): The ID of the user who owns the project.

        Raises:
            Exception: If the project is not found.
        """
        project = self.get_by_id(db_session, id, user_id)
        if not project:
            raise Exception("Project not found")
        db_session.delete(project)
        db_session.commit()

    def get_tools_for_project(
        self,
        db_session: Session,
        project_id: UUID,
        limit: int = None,
        offset: int = None,
    ) -> List[Tool]:
        """
        Retrieves a paginated list of tools associated with a project.

        Args:
            db_session (Session): The database session to use.
            project_id (UUID): The unique identifier of the project.
            limit (int): Maximum number of tools to return.
            offset (int): Number of tools to skip before starting to return results.

        Returns:
            tuple: A tuple containing:
                - list: List of dictionaries containing tool details (id, name, description)
                - int: Total count of tools for the project

        Raises:
            ValueError: If the project with the given ID is not found.
        """
        # Query the project and join the tools relationship
        project = db_session.query(Project).filter(
            Project.id == project_id).first()

        if not project:
            raise ValueError(f"Project with id {project_id} not found.")

        if offset is None or limit is None:
            tools = project.tools.all()
        else:
            tools = project.tools.offset(offset).limit(limit).all()

        tools_count = project.tools.count()

        return [{"id": tool.id,
                 "function_name": tool.function_name,
                 "name": tool.name,
                 "description": tool.description} for tool in tools], tools_count

    def modify_project_tools(self, db_session: Session, project_id: UUID, tools_id: Set[UUID]) -> None:
        """
        Update tool list of a project.

        Args:
            session (Session): SQLAlchemy session object.
            project_id (UUID): The UUID of the project.
            tool_id Set(UUID): Set of UUID of the tools to add.

        Returns:
            None
        """
        # Query the project and tool objects
        project = db_session.query(Project).filter(
            Project.id == project_id).first()

        if not project:
            raise ValueError(f"Project with id {project_id} not found.")

        # TODO: fix exception handling
        try:
            tools = db_session.query(Tool).filter(Tool.id.in_(tools_id)).all()
        except Exception as e:
            raise ValueError("Tools not found.")

        project.tools = tools

        # Commit the changes to the database
        db_session.commit()
