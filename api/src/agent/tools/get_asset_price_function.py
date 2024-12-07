from typing import Any
from langchain_core.tools import tool

@tool
def get_asset_price(asset: str) -> int:
    """
    Retrieves the mock price of a given asset in USD.

    Args:
        asset (str): The asset name (e.g., "ETH", "BTC").

    Returns:
        int: The mock price of the asset in USD.
    """
    # Mock price data for various assets
    mock_prices = {
        "ETH": 1800,
        "BTC": 35000,
        "USDT": 1,
        "DOGE": 0.08,
    }

    # Retrieve the price of the given asset or return 0 if not found
    return mock_prices.get(asset.upper(), 0)
