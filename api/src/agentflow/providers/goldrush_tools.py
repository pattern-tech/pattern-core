import json
import requests

from langchain.tools import tool
from typing import Any, Dict, List, Optional

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions


_config = Config.get_config()
_goldrush_config = Config.get_service_config(_config, "goldrush")


def _call_goldrush_api(url: str, params: Optional[Dict[str, Any]] = None) -> Dict:
    """
    Call the Goldrush API with the given URL and optional query parameters.

    Args:
        url (str): The endpoint URL.
        params (Optional[Dict[str, Any]]): Additional query parameters.

    Returns:
        Dict: Parsed JSON response.
    """
    api_key = _goldrush_config["api_key"]
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return json.loads(response.text)


@tool
@handle_exceptions
def get_wallet_activity(wallet_address: str, output_include: list[str]) -> List[Dict]:
    """
    Get activity across all chains for address

    Args:
        wallet_address (str): The wallet address to retrieve activity for.
        output_include (list[str]): List of keys to include in the final output.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - name, chain_id, is_testnet, db_schema_name, label, category_label, logo_url,
              black_logo_url, white_logo_url, color_theme, is_appchain, appchain_of, last_seen_at
    """
    base_url = _goldrush_config["url"]
    url = f"{base_url}/v1/address/{wallet_address}/activity/"
    data = _call_goldrush_api(url)
    results = data["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({item: result[item]
                             for item in result.keys() if item in output_include})
    return final_result


@tool
@handle_exceptions
def get_balance_for_address(wallet_address: str, output_include: list[str]) -> str:
    """
     fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address

    Args:
        wallet_address (str): The wallet address to retrieve balance for.
        output_include (list[str]):
            A list of field names to include in each activity item.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - contract_decimals, contract_name, contract_ticker_symbol, contract_address, contract_display_name,
              supports_erc, logo_url, logo_urls, last_transferred_at, native_token, type, is_spam, balance, balance_24h,
              quote_rate, quote_rate_24h, quote, quote_24h, pretty_quote, pretty_quote_24h, protocol_metadata.
    """
    base_url = _goldrush_config["url"]
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/address/{wallet_address}/balances_v2/"
    data = _call_goldrush_api(url)

    final_result = []
    for result in data["data"]["items"]:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_wallet_transactions(wallet_address: str, output_include: List[str], page: int = 0) -> List[Dict]:
    """
    Fetch transactions for a given wallet address (paginated)

    Args:
        wallet_address (str): The wallet address to retrieve transactions for.
        output_include (list[str]): A list of field names to include in each activity item.
        page (int): requested page starting from 0 Until get empty result

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - block_signed_at, block_height, block_hash, tx_hash, tx_offset, successful, from_address, miner_address,
              from_address_label, to_address, to_address_label, value, value_quote, pretty_value_quote, gas_metadata,
              gas_offered, gas_spent, gas_price, fees_paid, gas_quote, pretty_gas_quote, gas_quote_rate, explorers,
              log_events
    """
    base_url = _goldrush_config["url"]
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/address/{wallet_address}/transactions_v3/page/{page}/"
    data = _call_goldrush_api(url)

    final_result = []
    for result in data["data"]["items"]:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_transactions_summary(wallet_address: str) -> Dict:
    """
    Fetch a summary of transactions (earliest and latest) for a given wallet address.

    Args:
        wallet_address (str): The wallet address to retrieve transaction summary for.

    Returns:
        Dict: The transactions summary data.
    """
    base_url = _goldrush_config["url"]
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/address/{wallet_address}/transactions_summary/"
    data = _call_goldrush_api(url)
    return data["data"]["items"]


@tool
@handle_exceptions
def get_transaction_detail(tx_hash: str, output_include: List[str]) -> List[Dict]:
    """
    Fetch a single transaction including its decoded event logs

    Args:
        tx_hash (str): The transaction hash to retrieve details for.
        output_include (List[str]): A list of output fields to include in the result.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - block_signed_at, block_height, block_hash, tx_hash, tx_offset, successful, from_address, miner_address,
              from_address_label, to_address, to_address_label, value, value_quote, pretty_value_quote, gas_metadata,
              gas_offered, gas_spent, gas_price, fees_paid, gas_quote, pretty_gas_quote, gas_quote_rate, explorers,
              log_events, internal_transfers, state_changes, input_data
    """
    base_url = _goldrush_config["url"]
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/transaction_v2/{tx_hash}/"
    data = _call_goldrush_api(url)

    final_result = []
    for result in data["data"]["items"]:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_token_approvals(wallet_address: str, output_include: List[str]) -> Dict:
    """
    Fetch list of approvals across all token contracts categorized by spenders for a wallet’s assets

    Args:
        wallet_address (str): The wallet address to retrieve token approvals for.
        output_include (List[str]): A list of output fields to include in the result.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - token_address, token_address_label, ticker_symbol, contract_decimals, logo_url,
              quote_rate, balance, balance_quote, pretty_balance_quote, value_at_risk, value_at_risk_quote,
              pretty_value_at_risk_quote, spenders
    """
    base_url = _goldrush_config["url"]
    chain_name = "eth-mainnet"
    url = f"{base_url}/v1/{chain_name}/approvals/{wallet_address}/"
    data = _call_goldrush_api(url)

    final_result = []
    for result in data["data"]["items"]:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result
