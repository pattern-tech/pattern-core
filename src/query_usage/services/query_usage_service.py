from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple

from src.db.models import QueryUsage
from src.share.base_service import BaseService
from src.user.services.user_service import UserService
from src.share.staked_tokens import get_user_staked_tokens
from src.util.exceptions import NotFoundError, RateLimitError
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
        This is calculated as the sum of:
        1. User's whitelist allowance
        2. Allowance based on staked Morpheus tokens

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            int: The maximum number of queries the user is allowed to make.
        """
        user = self.user_service.get_user(db_session, user_id)

        # Get the user's base whitelist allowance using the dedicated method
        whitelist_allowance = self.get_user_whitelist_allowance(
            db_session, user_id)

        # Calculate additional allowance based on staked tokens
        token_based_allowance = self.get_user_token_based_allowance(
            db_session, user_id)

        # Total allowance is the sum of whitelist allowance and token-based allowance
        max_allowed_query = whitelist_allowance + token_based_allowance

        return max_allowed_query

    def get_user_token_based_allowance(self, db_session: Session, user_id: UUID) -> int:
        """
        Calculates a user's token-based query allowance based on their staked MOR tokens.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            int: The token-based query allowance (0 if no tokens are staked)
        """
        user = self.user_service.get_user(db_session, user_id)

        token_based_allowance = 0
        staked_morpheus = get_user_staked_tokens(
            wallet_address=user.wallet_address.lower(), provider="morpheus")

        if staked_morpheus > 0:
            usage_setting = self.get_usage_setting(db_session)
            for setting in usage_setting:
                if setting.provider == "morpheus":
                    token_based_allowance = setting.max_query * \
                        int(int(staked_morpheus) / 1e18)
                    break

        return token_based_allowance

    def get_user_whitelist_allowance(self, db_session: Session, user_id: UUID) -> int:
        """
        Retrieves the base query allowance for a user from the whitelist using a direct database query.

        Args:
            db_session (Session): The database session.
            user_id (UUID): The ID of the user.

        Returns:
            int: The base query allowance from the whitelist (default: 0 if not whitelisted)
        """
        # Use the repository to directly query the database for whitelist allowance
        allowance = self.repository.get_user_whitelist_allowance(
            db_session, user_id)

        # Return the allowance if found, otherwise return 0
        return allowance if allowance is not None else 0

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
