from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.share.base_repository import BaseRepository
from src.db.models import Workspace


class WorkspaceRepository(BaseRepository[Workspace]):
    """
    Repository class for handling CRUD operations on the Workspace model.
    """

    def get_by_id(
        self, db_session: Session, id: UUID, user_id: UUID
    ) -> Optional[Workspace]:
        """
        Retrieves a workspace by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the workspace.
            user_id (UUID): The unique identifier of the user.

        Returns:
            Optional[Workspace]: The workspace if found, otherwise None.
        """
        return (
            db_session.query(Workspace)
            .filter(Workspace.id == id, Workspace.user_id == user_id)
            .first()
        )

    def list(self, db_session: Session, user_id: UUID) -> List[Workspace]:
        """
        Retrieves all workspaces for a given user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.

        Returns:
            List[Workspace]: A list of workspaces owned by the user.
        """
        return db_session.query(Workspace).filter(Workspace.user_id == user_id).all()

    def create(self, db_session: Session, workspace: Workspace) -> Workspace:
        """
        Creates a new workspace.

        Args:
            db_session (Session): The database session to use.
            workspace (Workspace): The workspace instance to add.

        Returns:
            Workspace: The created workspace instance with updated attributes.
        """
        db_session.add(workspace)
        db_session.commit()
        db_session.refresh(workspace)
        return workspace

    def update(
        self, db_session: Session, id: UUID, workspace_data: dict, user_id: UUID
    ) -> Workspace:
        """
        Updates an existing workspace.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the workspace to update.
            workspace_data (dict): A dictionary of fields to update.
            user_id (UUID): The unique identifier of the user.

        Raises:
            Exception: If the workspace is not found or not owned by the user.

        Returns:
            Workspace: The updated workspace instance.
        """
        workspace = self.get_by_id(db_session, id, user_id)
        if not workspace:
            raise Exception("Workspace not found or not owned by user")
        for key, value in workspace_data.items():
            setattr(workspace, key, value)
        db_session.commit()
        db_session.refresh(workspace)
        return workspace

    def delete(self, db_session: Session, id: UUID, user_id: UUID) -> None:
        """
        Deletes a workspace by its ID and user ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the workspace to delete.
            user_id (UUID): The unique identifier of the user.

        Raises:
            Exception: If the workspace is not found or not owned by the user.
        """
        workspace = self.get_by_id(db_session, id, user_id)
        if not workspace:
            raise Exception("Workspace not found or not owned by user")
        db_session.delete(workspace)
        db_session.commit()
