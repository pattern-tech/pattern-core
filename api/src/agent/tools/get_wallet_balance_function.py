from typing import Dict, List
from langchain_core.tools import tool


@tool
def get_wallet_balance(wallet_address: str) -> List[Dict[str, int]]:
    """
    Retrieves the assets and their corresponding balances for a given wallet address.

    Args:
        wallet_address (str): The wallet address for which to retrieve the asset balances.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary represents an asset
        and its balance. Example:
            [
                {"asset": "ETH", "balance": 2},
                {"asset": "BTC", "balance": 0.5}
            ]
    """

    return [
        {"asset": "ETH", "balance": 2.5},
        {"asset": "BTC", "balance": 0.75},
        {"asset": "USDT", "balance": 500.0},
        {"asset": "ADA", "balance": 1200.0},
        {"asset": "SOL", "balance": 10.0},
        {"asset": "DOGE", "balance": 15000.0},
    ]
