from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.db.models import Project
from src.project.repositories.project_repository import ProjectRepository


class ProjectService:
    """
    Service class for handling project-related business logic.
    """

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(
            self, db_session: Session, name: str, user_id: UUID, workspace_id: UUID
    ) -> Project:
        """
        Creates a new project.

        Args:
            db_session (Session): The database session.
            name (str): The name of the project.
            user_id (UUID): The ID of the user who owns the project.
            workspace_id (UUID): The ID of the workspace the project belongs to.

        Returns:
            Project: The created project instance.
        """
        project = Project(name=name, user_id=user_id,
                          workspace_id=workspace_id)
        return self.repository.create(db_session, project)

    def get_project(
        self, db_session: Session, project_id: UUID, user_id: UUID
    ) -> Project:
        """
        Retrieves a project by its ID.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to retrieve.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            Project: The project instance.

        Raises:
            Exception: If the project is not found.
        """
        project = self.repository.get_by_id(db_session, project_id, user_id)
        if not project:
            raise Exception("Project not found")
        return project

    def list_projects(
        self, db_session: Session, user_id: UUID
    ) -> List[Project]:
        """
        Lists all projects owned by a specific user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user who owns the projects.

        Returns:
            List[Project]: A list of Project instances.
        """
        return self.repository.get_all(db_session, user_id)

    def update_project(
        self, db_session: Session, project_id: UUID, data: dict, user_id: UUID
    ) -> Project:
        """
        Updates a project with the given data.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to update.
            data (dict): A dictionary containing the fields to update.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            Project: The updated project instance.
        """
        return self.repository.update(db_session, project_id, data, user_id)

    def delete_project(
        self, db_session: Session, project_id: UUID, user_id: UUID
    ) -> None:
        """
        Deletes a project.

        Args:
            db_session (Session): The database session.
            project_id (UUID): The ID of the project to delete.
            user_id (UUID): The ID of the user who owns the project.

        Returns:
            None
        """
        self.repository.delete(db_session, project_id, user_id)
