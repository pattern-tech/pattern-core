from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.workspace.services.workspace_service import WorkspaceService
from src.db.models import UserModel
from src.user.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, db_session: Session, email: str, password: str) -> UserModel:
        """
        Creates a new user.

        Args:
            db_session (Session): The database session.
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            UserModel: The created user instance.
        """
        _user = UserModel(email=email, password=password)
        user = self.repository.create(db_session, _user)

        return user

    def get_user(self, db_session: Session, user_id: UUID) -> UserModel:
        """
        Retrieves a user by their ID.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user to retrieve.

        Returns:
            UserModel: The User instance.

        Raises:
            Exception: If the user is not found.
        """
        user = self.repository.get_by_id(db_session, user_id)
        if not user:
            raise Exception("User not found")
        return user

    def list_users(self, db_session: Session) -> List[UserModel]:
        """
        Lists all users.

        Args:
            db_session (Session): The database session.

        Returns:
            List[UserModel]: A list of User instances.
        """
        return self.repository.get_all(db_session)

    def update_user(self, db_session: Session, user_id: UUID, data: dict) -> UserModel:
        """
        Updates a user with the given data.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user to update.
            data (dict): A dictionary containing the fields to update.

        Returns:
            UserModel: The updated User instance.
        """
        return self.repository.update(db_session, user_id, data)

    def delete_user(self, db_session: Session, user_id: UUID) -> None:
        """
        Deletes a user.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user to delete.

        Returns:
            None
        """
        self.repository.delete(db_session, user_id)
