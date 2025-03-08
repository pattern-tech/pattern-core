from uuid import UUID
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from src.db.models import QueryUsage, UsageSetting
from src.share.base_repository import BaseRepository


class QueryUsageRepository(BaseRepository[QueryUsage]):
    """
    Repository class for handling CRUD operations on the QueryUsage model.
    """

    def create(self, db_session: Session, query_usage: QueryUsage) -> QueryUsage:
        """
        Creates a new query usage.

        Args:
            db_session (Session): The database session to use.
            query_usage (QueryUsage): The query usage instance to add.

        Returns:
            QueryUsage: The created query usage instance with updated attributes.
        """
        db_session.add(query_usage)
        db_session.commit()
        db_session.refresh(query_usage)
        return query_usage

    def get_by_id(self, db_session: Session, id: UUID) -> Optional[QueryUsage]:
        """
        Retrieves a query usage by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the query usage.

        Returns:
            Optional[QueryUsage]: The query usage if found, otherwise None.
        """
        return db_session.query(QueryUsage).filter(QueryUsage.id == id).first()

    def get_all(self, db_session: Session) -> List[QueryUsage]:
        """
        Retrieves all query usages.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[QueryUsage]: A list of all query usages.
        """
        return db_session.query(QueryUsage).all()

    def get_user_query_usage(self, db_session: Session, user_id: UUID,
                             provider: str = None, duration: datetime = None) -> List[QueryUsage]:
        """
        Retrieves all query usages for a specific user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.
            provider (str): The provider of the query usage to filter by.
            duration (datetime): The duration date of the query usage to filter by.

        Returns:
            List[QueryUsage]: A list of all query usages for the user.
        """
        query = db_session.query(QueryUsage).filter(
            QueryUsage.user_id == user_id)
        if provider:
            query = query.filter(QueryUsage.provider == provider)
        if duration:
            query = query.filter(
                (datetime.now() - QueryUsage.created_at) <= duration)
        return query.all()

    def get_usage_setting(self, db_session: Session) -> List[UsageSetting]:
        """
        Retrieves all usage settings.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[UsageSetting]: A list of all usage settings.
        """
        return db_session.query(UsageSetting).all()

    def update(self, db_session, id: UUID) -> None:
        pass

    def delete(self, db_session, id: UUID) -> None:
        pass
