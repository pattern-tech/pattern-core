from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from src.share.base_repository import BaseRepository
from src.db.models import QueryUsage, UsageSetting, UserModel


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
                             provider: str = None, duration: timedelta = None) -> List[QueryUsage]:
        """
        Retrieves all query usages for a specific user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.
            provider (str): The provider of the query usage to filter by.
            duration (timedelta): The duration to filter query usage by (e.g., last 24 hours).

        Returns:
            List[QueryUsage]: A list of all query usages for the user.
        """
        query = db_session.query(QueryUsage).filter(
            QueryUsage.user_id == user_id)
        if provider:
            query = query.filter(QueryUsage.provider == provider)
        if duration:
            time_threshold = datetime.now() - duration
            query = query.filter(QueryUsage.created_at >= time_threshold)
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

    def get_user_query_count_for_today(self, db_session: Session, user_id: UUID, provider: str = None) -> Tuple[int, Optional[datetime]]:
        """
        Retrieves the count of queries made by a user today, where 'today' is defined as a 24-hour period
        starting from the user's account creation time.

        For example, if a user was created at 12:00 PM on July 1, 2000, then 'today' for that user
        would be from 12:00 PM yesterday to 12:00 PM today.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.
            provider (str, optional): The provider to filter by. Defaults to None.

        Returns:
            Tuple[int, Optional[datetime]]: A tuple containing the count of queries, the timestamp of the oldest query
            and next reset time.
        """
        # Get the user's creation time
        user = db_session.query(UserModel).filter(
            UserModel.id == user_id).first()
        if not user:
            return 0, None

        # Calculate the start of the user's 'today' (24 hours from their creation time)
        creation_time = user.created_at.replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)

        # Calculate the day offset (how many days have passed since creation)
        days_since_creation = (current_time - creation_time).days

        # Calculate the start and end of the user's 'today'
        today_start = creation_time + timedelta(days=days_since_creation)
        today_end = today_start + timedelta(days=1)

        # Query to count the user's queries for today
        query = db_session.query(func.count(QueryUsage.id).label('count'), func.min(QueryUsage.created_at).label('oldest'))\
            .filter(QueryUsage.user_id == user_id)\
            .filter(QueryUsage.created_at >= today_start)\
            .filter(QueryUsage.created_at < today_end)

        if provider:
            query = query.filter(QueryUsage.provider == provider)

        result = query.first()

        result_count = result.count if result else 0
        result_oldest = result.oldest if result and result.count > 0 else None
        next_reset = today_end

        return result_count, result_oldest, next_reset

    def get_user_whitelist_allowance(self, db_session: Session, user_id: UUID) -> Optional[int]:
        """
        Retrieves the user's whitelist max_query allowance directly from the database.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.

        Returns:
            Optional[int]: The user's max query allowance from the whitelist, or None if not whitelisted.
        """
        from src.db.models import WhiteList

        whitelist_entry = db_session.query(WhiteList.max_query)\
            .filter(WhiteList.user_id == user_id)\
            .first()

        return whitelist_entry.max_query if whitelist_entry else None

    def update(self, db_session, id: UUID) -> None:
        pass

    def delete(self, db_session, id: UUID) -> None:
        pass
