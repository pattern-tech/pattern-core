from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple

from src.db.models import QueryUsage
from src.share.base_service import BaseService
from src.user.services.user_service import UserService
from src.share.staked_tokens import get_user_staked_tokens
from src.util.execptions import NotFoundError, RateLimitError
from src.query_usage.repositories.query_usage_repository import QueryUsageRepository


class QueryUsageService(BaseService):
    def __init__(self):
        self.repository = QueryUsageRepository()
        self.user_service = UserService()

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
        query_usage = self.repository.get_by_id(db_session, id)
        if not query_usage:
            raise NotFoundError("Query usage not found")

        return query_usage

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

    def get_user_max_query_allowance(self, db_session: Session, user_id: UUID) -> int:
        """
        Retrieves the maximum number of queries a user is allowed to make.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            int: The maximum number of queries the user is allowed to make.

        Raises:
            Exception: If the user has not staked any Morpheus tokens.
        """
        user = self.user_service.get_user(db_session, user_id)

        whitelist = self.user_service.get_whitelist(db_session)

        # check user payment
        for wl in whitelist:
            if str(user_id) == str(wl.user_id):
                max_allowed_query = wl.max_query
                return max_allowed_query

        staked_morpheus = get_user_staked_tokens(
            wallet_address=user.wallet_address, provider="morpheus")

        if staked_morpheus == 0:
            raise RateLimitError(
                "You need to stake Morpheus tokens to use this service")

        usage_setting = self.get_usage_setting(
            db_session)

        max_allowed_query = 0
        for setting in usage_setting:
            if setting.provider == "morpheus":
                max_allowed_query = setting.max_query * \
                    (int(staked_morpheus) / 1e18)
                break

        return max_allowed_query

    def get_user_query_count_for_today(self, db_session: Session, user_id: UUID, provider: Optional[str] = None) -> Tuple[int, Optional[datetime]]:
        """
        Retrieves the count of queries made by a user today and the timestamp of the oldest query.

        'Today' is defined as a 24-hour period starting from the user's account creation time.

        Args:
            db_session (Session): The database session to use.
            user_id (UUID): The unique identifier of the user.
            provider (str, optional): The provider to filter by. Defaults to None.

        Returns:
            Tuple[int, Optional[datetime]]: A tuple containing the count of queries and 
                                           the timestamp of the oldest query.
        """
        return self.repository.get_user_query_count_for_today(db_session, user_id, provider)

    def check_user_eligibility(self, db_session: Session, user_id: UUID, max_query_allowance: int) -> bool:
        """
        Checks if a user is eligible to make a query based on their daily query limit.
        If a user has exceeded their daily limit for the current day (since midnight UTC),
        they won't be allowed to chat with the model until the next day.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.
            max_query_allowance (int): The number of queries the user is allowed to make per day.

        Returns:
            bool: True if the user is eligible, False otherwise.
        """
        # Get the count of queries for today and the timestamp of the oldest query
        query_count, _, _ = self.get_user_query_count_for_today(
            db_session, user_id, "morpheus"
        )

        # If the user has exceeded their daily limit
        if query_count >= max_query_allowance:
            return False

        return True
