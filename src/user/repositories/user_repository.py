from uuid import UUID
from typing import Optional
from sqlalchemy.orm import Session, load_only

from src.db.models import UserModel, WhiteList
from src.share.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    """
    Repository class for handling CRUD operations on the UserModel.
    """

    def get_by_id(self, db_session: Session, user_id: UUID = None) -> Optional[UserModel]:
        """
        Retrieves a user by their ID.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.

        Returns:
            Optional[UserModel]: The user if found, otherwise None.
        """
        return db_session.query(UserModel).options(
            load_only(UserModel.id, UserModel.wallet_address,
                      UserModel.email, UserModel.chain_id)
        ).filter(UserModel.id == user_id).first()

    def get_by_wallet_address(self, db_session: Session, wallet_address: str) -> Optional[UserModel]:
        """
        Retrieves a user by their wallet address.

        Args:
            db_session (Session): The database session to use.
            wallet_address (str): The wallet address of the user.

        Returns:
            Optional[UserModel]: The user if found, otherwise None.
        """
        return db_session.query(UserModel).options(
            load_only(UserModel.id, UserModel.wallet_address,
                      UserModel.email, UserModel.chain_id)
        ).filter(UserModel.wallet_address == wallet_address).first()

    def get_all(self, db_session: Session) -> list[UserModel]:
        """
        Retrieves all users.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[UserModel]: A list of all users.
        """
        return db_session.query(UserModel).options(
            load_only(UserModel.id, UserModel.wallet_address,
                      UserModel.email, UserModel.chain_id)).all()

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

    def update(self, db_session: Session, user_id: UUID, user_data: dict) -> UserModel:
        """
        Updates an existing user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user to update.
            user_data (dict): A dictionary of fields to update.

        Returns:
            UserModel: The updated user instance.
        """
        user = self.get_by_id(db_session, user_id)
        if not user:
            raise Exception("User not found")
        for key, value in user_data.items():
            setattr(user, key, value)
        db_session.commit()
        db_session.refresh(user)
        return user

    def delete(self, db_session: Session, user_id: UUID = None) -> None:
        """
        Deletes a user by their ID.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user to delete.

        Raises:
            Exception: If the user is not found.
        """
        user = self.get_by_id(db_session, user_id)
        if not user:
            raise Exception("User not found")
        db_session.delete(user)
        db_session.commit()

    def get_whitelist(self, db_session: Session) -> list[WhiteList]:
        """
        Retrieves all whitelisted users.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[WhiteList]: A list of all whitelisted users.
        """
        return db_session.query(WhiteList).all()

    def create_whitelist_entry(self, db_session: Session, user_id: UUID, max_query: int = 20) -> WhiteList:
        """
        Creates a whitelist entry for a user with a default max query limit of 20.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user to whitelist.
            max_query (int): The maximum number of queries allowed for this user.

        Returns:
            WhiteList: The created whitelist entry.
        """
        whitelist_entry = WhiteList(user_id=user_id, max_query=max_query)
        db_session.add(whitelist_entry)
        db_session.commit()
        db_session.refresh(whitelist_entry)
        return whitelist_entry
