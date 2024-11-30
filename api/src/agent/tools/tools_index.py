from typing import Callable, Optional

from api.src.agent.tools.get_wallet_balance_function import get_wallet_balance
from src.agent.tools.get_asset_price_function import get_asset_price
from src.agent.tools.weather_function import get_weather

tool_function_index = [get_weather, get_wallet_balance, get_asset_price]


def get_tool_by_name(name: str) -> Optional[Callable]:
    """Gets a tool function by name if it exists."""

    for func in tool_function_index:
        if getattr(func, "name", None) == name:
            return func
    return None
