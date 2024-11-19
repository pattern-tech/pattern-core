from typing import List
from src.workspace.repository.workspace_repository import WorkspaceRepository
from src.share.base_service import BaseService
from src.db.models import Workspace
from sqlalchemy.orm import Session
from uuid import UUID


class WorkspaceService(BaseService):
    def __init__(self, repository: WorkspaceRepository):
        self.repository = repository

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
        workspace = self.repository.get_by_id(db_session, workspace_id, user_id)
        if not workspace:
            raise Exception("Workspace not found or not owned by user")
        return workspace

    def list_workspaces(self, db_session: Session, user_id: UUID) -> List[Workspace]:
        """
        Lists all workspaces owned by a user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user whose workspaces are to be listed.

        Returns:
            List[Workspace]: A list of Workspace instances owned by the user.
        """
        return self.repository.list(db_session, user_id)

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
