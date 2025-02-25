from uuid import UUID
from typing import Optional, List, Set
from sqlalchemy.orm import Session

from src.db.models import Project
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
