from typing import Callable, Optional

from src.agent.tools.google_search_function import search_on_web_by_query
from src.agent.tools.reddit_search_function import search_on_reddit
from src.agent.tools.linkedin_search_function import search_on_linkedin, get_linkedin_profile_by_url
from src.agent.tools.scrape_website_function import get_content_of_website
from src.agent.tools.weather_function import get_weather
from src.agent.tools.latest_news_function import get_latest_news
from src.agent.tools.get_current_datetime_function import get_current_datetime
from src.agent.tools.get_asset_price_function import get_asset_price
from src.agent.tools.get_wallet_balance_function import get_wallet_balance
from src.agent.tools.math_function import add, multiply

tool_function_index = [
    search_on_web_by_query,
    search_on_linkedin,
    get_linkedin_profile_by_url,
    search_on_reddit,
    get_content_of_website,
    get_latest_news,
    get_weather,
    get_current_datetime,
    get_asset_price,
    get_wallet_balance,
    multiply,
    add,
]


def get_tool_by_name(name: str) -> Optional[Callable]:
    """Get a tool function by name if it exists."""

    for func in tool_function_index:
        if getattr(func, "name", None) == name:
            return func
    return None


def get_all_tools() -> list[Callable]:
    """Get all tool functions."""

    return tool_function_index
