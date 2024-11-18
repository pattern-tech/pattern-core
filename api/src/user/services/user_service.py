from uuid import UUID
from sqlalchemy.orm import Session
from src.db.models import UserModel
from src.db.sql_alchemy import Database
from sqlalchemy import select

database = Database()


class UserService:
    def get_user_by_id(
        self,
        user_id: UUID,
        db: Session,
    ):
        """
        Fetch a user by their ID.

        :param session: SQLAlchemy session object.
        :param user_id: UUID of the user.
        :return: A dictionary containing user details (excluding the password) or None if not found.
        """
        stmt = select(UserModel.id, UserModel.email).where(UserModel.id == user_id)
        result = db.execute(stmt).one_or_none()
        if result:
            return {"id": str(result.id), "email": result.email}
        return None
