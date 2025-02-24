import os
import json
import requests

from langchain.tools import tool
from typing import Any, Dict, List, Optional

from src.agentflow.utils.shared_tools import handle_exceptions


def _get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Returns:
        str: The API key.

    Raises:
        Exception: If the API key is not found.
    """
    api_key = os.getenv("GOLDRUSH_API_KEY")
    if not api_key:
        raise Exception("No API key found for Goldrush.")
    return api_key


def _call_goldrush_api(url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
    """
    Call the Goldrush API with the given URL and optional query parameters.

    Args:
        url (str): The endpoint URL.
        params (Optional[Dict[str, Any]]): Additional query parameters.

    Returns:
        Dict: Parsed JSON response.
    """
    api_key = _get_api_key()
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return json.loads(response.text)


@tool
@handle_exceptions
def get_wallet_activity(wallet_address: str) -> List[Dict]:
    """
    Fetch wallet activity for a given wallet address using the Goldrush API.

    Args:
        wallet_address (str): The wallet address to retrieve activity for.

    Returns:
        List[Dict]: List of wallet activity items.
    """
    base_url = os.getenv("GOLDRUSH_URL")
    url = f"{base_url}/v1/address/{wallet_address}/activity/"
    data = _call_goldrush_api(url)
    return data["data"]["items"]


@tool
@handle_exceptions
def get_balance_for_address(
    wallet_address: str, no_spam: bool = True, currency: str = "USD"
) -> str:
    """
    Fetch the balance for a given wallet address on a specific chain using the Goldrush API.

    Args:
        wallet_address (str): The wallet address to retrieve balance for.
        no_spam (bool): Flag to indicate spam filtering; defaults to True.
        currency (str): The quote currency for balance conversion.
                        Available options: ["USD", "CAD", "EUR", "SGD", "INR", "JPY",
                        "VND", "CNY", "KRW", "RUB", "TRY", "NGN", "ARS", "AUD", "CHF", "GBP"].

    Returns:
        str: The balance in the specified currency.

    Raises:
        ValueError: If an invalid currency is provided.
    """
    valid_currencies = [
        "USD", "CAD", "EUR", "SGD", "INR", "JPY", "VND",
        "CNY", "KRW", "RUB", "TRY", "NGN", "ARS", "AUD", "CHF", "GBP"
    ]
    if currency not in valid_currencies:
        raise ValueError(
            f"Invalid currency. Please choose from: {', '.join(valid_currencies)}"
        )

    base_url = os.getenv("GOLDRUSH_URL")
    chain_name = "eth-mainnet"
    no_spam_param = "true" if no_spam else "false"
    url = (
        f"{base_url}/v1/{chain_name}/address/{wallet_address}/balances_v2/"
        f"?quote-currency={currency}&no-spam={no_spam_param}"
    )
    data = _call_goldrush_api(url)
    # Assuming the balance is in the first item in the list
    return data["data"]["items"][0]["pretty_quote"]


@tool
@handle_exceptions
def get_wallet_transactions(wallet_address: str, page: int) -> List[Dict]:
    """
    Fetch transactions for a given wallet address using the Goldrush API.

    Args:
        wallet_address (str): The wallet address to retrieve transactions for.
        page (int): The page number of transactions to retrieve.

    Returns:
        List[Dict]: A paginated list of transaction items (first 10 items of the page).
    """
    base_url = os.getenv("GOLDRUSH_URL")
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/address/{wallet_address}/transactions_v3/page/{page}/"
    data = _call_goldrush_api(url)
    return data["data"]["items"][:10]


@tool
@handle_exceptions
def get_transactions_summary(wallet_address: str) -> Dict:
    """
    Fetch a summary of transactions (earliest and latest) for a given wallet address using the Goldrush API.

    Args:
        wallet_address (str): The wallet address to retrieve transaction summary for.

    Returns:
        Dict: The transactions summary data.
    """
    base_url = os.getenv("GOLDRUSH_URL")
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/address/{wallet_address}/transactions_summary/"
    data = _call_goldrush_api(url)
    return data["data"]["items"]


@tool
@handle_exceptions
def get_transaction_detail(tx_hash: str) -> List[Dict]:
    """
    Fetch details of a specific transaction using the Goldrush API.

    Args:
        tx_hash (str): The transaction hash to retrieve details for.

    Returns:
        List[Dict]: A list of decoded log events containing function names and parameters.
    """
    base_url = os.getenv("GOLDRUSH_URL")
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/transaction_v2/{tx_hash}/"
    data = _call_goldrush_api(url)
    final_result = []
    for result in data["data"]["items"]:
        for event in result.get("log_events", []):
            decoded = event.get("decoded")
            if decoded:
                final_result.append({
                    "function_name": decoded.get("name"),
                    "function_params": decoded.get("params"),
                })
    return final_result


@tool
@handle_exceptions
def get_token_approvals(wallet_address: str) -> Dict:
    """
    Retrieve a list of token approvals for a wallet across all token contracts using the Goldrush API.

    Args:
        wallet_address (str): The wallet address to retrieve token approvals for.

    Returns:
        Dict: The token approvals data.
    """
    base_url = os.getenv("GOLDRUSH_URL")
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/approvals/{wallet_address}/"
    data = _call_goldrush_api(url)
    return data["data"]["items"]
