from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from src.db.models import UserModel, WhiteList, UsageSetting
from src.user.repositories.user_repository import UserRepository


class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_user(self, db_session: Session, wallet_address: str, chain_id: int, email: str = None, password: str = None,
                    ) -> UserModel:
        """
        Creates a new user and automatically whitelists them with the default max query value from database.

        Args:
            db_session (Session): The database session.
            wallet_address (str): The wallet address of the user.
            chain_id (int): The chain ID of the user.
            email (str): The email of the user.
            password (str): The password of the user.

        Returns:
            UserModel: The created user instance.
        """
        if email:
            email = email.lower()
        _user = UserModel(wallet_address=wallet_address,
                          chain_id=chain_id, email=email, password=password)
        user = self.repository.create(db_session, _user)

        default_max_query = 0
        usage_settings = db_session.query(UsageSetting).filter(
            UsageSetting.provider == "pattern").first()
        if usage_settings:
            default_max_query = usage_settings.max_query

        # Automatically whitelist the user with the default query credits from database
        self.repository.create_whitelist_entry(
            db_session, user.id, max_query=default_max_query)

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

    def get_user_by_wallet_address(self, wallet_address: str, db_session: Session) -> UserModel:
        """
        Retrieves a user by their wallet address.

        Args:
            wallet_address (str): The wallet address of the user.
            db_session (Session): The database session.

        Returns:
            UserModel: The User instance.

        Raises:
            Exception: If the user is not found.
        """
        user = self.repository.get_by_wallet_address(
            db_session, wallet_address)

        return user

    def get_whitelist(self, db_session: Session) -> List[UserModel]:
        """
        Retrieves all whitelisted users.

        Args:
            db_session (Session): The database session.

        Returns:
            List[UserModel]: A list of whitelisted User instances.
        """
        return self.repository.get_whitelist(db_session)

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
