from uuid import UUID
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session

from src.db.models import QueryUsage
from src.share.base_service import BaseService
from src.query_usage.repositories.query_usage_repository import QueryUsageRepository


class QueryUsageService(BaseService):
    def __init__(self):
        self.repository = QueryUsageRepository()

    def create_query_usage(self, db_session: Session, query_usage: QueryUsage) -> QueryUsage:
        """
        Creates a new query usage.

        Args:
            db_session (Session): The database session to use.
            query_usage (QueryUsage): The query usage instance to add.

        Returns:
            QueryUsage: The created query usage instance with updated attributes.
        """
        return self.repository.create(db_session, query_usage)

    def get_query_usage(self, db_session: Session, id: UUID) -> Optional[QueryUsage]:
        """
        Retrieves a query usage by its ID.

        Args:
            db_session (Session): The database session to use.
            id (UUID): The unique identifier of the query usage.

        Returns:
            Optional[QueryUsage]: The query usage if found, otherwise None.
        """
        return self.repository.get_by_id(db_session, id)

    def get_all_query_usages(
            self, db_session: Session, user_id: UUID, provider: str = None, duration: datetime = None) -> List[QueryUsage]:
        """
        Retrieves all query usages for a specific user.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.
            provider (str): The provider of the query usage to filter by.
            duration (datetime): The duration of the query usage to filter by.

        Returns:
            List[QueryUsage]: A list of all query usages for the user.
        """
        return self.repository.get_user_query_usage(db_session, user_id, provider, duration)

    def get_usage_setting(self, db_session: Session) -> List[QueryUsage]:
        """
        Retrieves all usage settings.

        Args:
            db_session (Session): The database session to use.

        Returns:
            List[UsageSetting]: A list of all usage settings.
        """
        return self.repository.get_usage_setting(db_session)
