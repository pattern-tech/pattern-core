from uuid import UUID
from typing import List

from sqlalchemy import join, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from src.db.models import Project, Workspace
from src.share.base_service import BaseService
from src.workspace.repositories.workspace_repository import WorkspaceRepository


class WorkspaceService(BaseService):
    def __init__(self):
        self.repository = WorkspaceRepository()

    def create_workspace(
        self, db_session: Session, name: str, user_id: UUID
    ) -> Workspace:
        """
        Creates a new Workspace.

        Args:
            db_session (Session): The database session.
            name (str): The name of the workspace.
            user_id (UUID): The ID of the user who owns the workspace.

        Returns:
            Workspace: The created Workspace instance.
        """
        workspace = Workspace(name=name, user_id=user_id)
        return self.repository.create(db_session, workspace)

    def get_workspace(
        self, db_session: Session, workspace_id: UUID, user_id: UUID
    ) -> Workspace:
        """
        Retrieves a workspace by its ID and verifies ownership.

        Args:
            db_session (Session): The database session.
            workspace_id (UUID): The ID of the workspace to retrieve.
            user_id (UUID): The ID of the user who owns the workspace.

        Returns:
            Workspace: The Workspace instance.

        Raises:
            Exception: If the workspace is not found or the user does not own it.
        """
        workspace_query = (
            db_session.query(Workspace, Project.id, Project.name)
            .join(Project, Workspace.id == Project.workspace_id)
            .filter(Workspace.id == workspace_id, Workspace.user_id == user_id)
            .all()
        )
        if not workspace_query:
            raise Exception("Workspace not found or no projects available")

        # Transform the result into a structured dictionary
        workspace_data = {
            "id": workspace_query[0][0].id,
            "name": workspace_query[0][0].name,
            "projects": [
                {"id": project_id, "name4": project_name}
                for _, project_id, project_name in workspace_query
            ],
        }

        return workspace_data

    def get_all_workspaces(self, db_session: Session, user_id: UUID) -> List[Workspace]:
        """
        Lists all workspaces owned by a user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user whose workspaces are to be listed.

        Returns:
            List[Workspace]: A list of Workspace instances owned by the user.
        """
        return self.repository.get_all(db_session, user_id)

    def update_workspace(
        self, db_session: Session, workspace_id: UUID, data: dict, user_id: UUID
    ) -> Workspace:
        """
        Updates a workspace with the given data.

        Args:
            db_session (Session): The database session.
            workspace_id (UUID): The ID of the workspace to update.
            data (dict): A dictionary containing the fields to update.
            user_id (UUID): The ID of the user who owns the workspace.

        Returns:
            Workspace: The updated Workspace instance.
        """
        return self.repository.update(db_session, workspace_id, data, user_id)

    def delete_workspace(
        self, db_session: Session, workspace_id: UUID, user_id: UUID
    ) -> None:
        """
        Deletes a workspace.

        Args:
            db_session (Session): The database session.
            workspace_id (UUID): The ID of the workspace to delete.
            user_id (UUID): The ID of the user who owns the workspace.

        Returns:
            None
        """
        self.repository.delete(db_session, workspace_id, user_id)
