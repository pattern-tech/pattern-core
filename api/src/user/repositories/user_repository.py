from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session

from src.db.models import UserModel
from src.share.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """
    Repository class for handling CRUD operations on the UserModel.
    """

    def get_by_id(self, db_session: Session, id: UUID, user_id: UUID = None) -> Optional[UserModel]:
        """
        Retrieves a user by their ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the user.

        Returns:
            Optional[UserModel]: The user if found, otherwise None.
        """
        return db_session.query(UserModel).filter(UserModel.id == id).first()

    def get_all(self, db_session: Session, user_id: UUID = None) -> list[UserModel]:
        """
        Retrieves all users.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[UserModel]: A list of all users.
        """
        return db_session.query(UserModel).all()

    def create(self, db_session: Session, user: UserModel) -> UserModel:
        """
        Creates a new user.

        Args:
            db_session (Session): The database session to use.
            user (UserModel): The user instance to add.

        Returns:
            UserModel: The created user instance.
        """
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def update(self, db_session: Session, id: UUID, user_data: dict, user_id: UUID = None) -> UserModel:
        """
        Updates an existing user.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the user to update.
            user_data (dict): A dictionary of fields to update.

        Returns:
            UserModel: The updated user instance.
        """
        user = self.get_by_id(db_session, id)
        if not user:
            raise Exception("User not found")
        for key, value in user_data.items():
            setattr(user, key, value)
        db_session.commit()
        db_session.refresh(user)
        return user

    def delete(self, db_session: Session, id: UUID, user_id: UUID = None) -> None:
        """
        Deletes a user by their ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the user to delete.

        Raises:
            Exception: If the user is not found.
        """
        user = self.get_by_id(db_session, id)
        if not user:
            raise Exception("User not found")
        db_session.delete(user)
        db_session.commit()
