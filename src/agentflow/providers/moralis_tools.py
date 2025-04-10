import requests

from typing import Any
from moralis import evm_api
from langchain.tools import tool

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions

_config = Config.get_config()
_moralis_config = Config.get_service_config(_config, "MORALIS")

_MORALIS_URL = "https://deep-index.moralis.io/api/v2"

@tool
@handle_exceptions
def get_wallet_active_chains(wallet_address: str, output_include: list[str]) -> list[dict[str, Any]]:
    """
    Get active chains for a wallet address across all chains

    Args:
        wallet_address (str): Ethereum wallet address
        output_include (list[str]):
            A list of field names to include in in the output.


    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - chain, chain_id, first_transaction, last_transaction
    """
    params = {
        "address": wallet_address
    }

    result = evm_api.wallets.get_wallet_active_chains(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    results = result["active_chains"]
    final_results = []
    for result in results:
        final_results.append({item: result[item]
                              for item in result.keys() if item in output_include})
    return final_results


@tool
@handle_exceptions
def get_wallet_token_balances(wallet_address: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Get token balances for a specific wallet address and their token prices in USD. (paginated)
    apply decimal conversion for balance

    Args:
        wallet_address (str): Ethereum wallet address
        output_include (list[str]): A list of field names to include in the output.
        cursor (str): The cursor returned in the previous response (used for getting the next page). end of page cursor is None


    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - token_address, symbol, name, logo, thumbnail, decimals, balance, balance_formatted,
              usd_price, usd_price_24hr_percent_change, usd_price_24hr_usd_change, usd_value,
              usd_value_24hr_usd_change, native_token, portfolio_percentage
    """
    params = {
        "chain": "eth",
        "address": wallet_address
    }

    if cursor:
        params["cursor"] = cursor

    api_result = evm_api.wallets.get_wallet_token_balances_price(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    results = api_result["result"]
    final_results = []
    for result in results:
        final_results.append({item: result[item]
                              for item in result.keys() if item in output_include})

    return {"cursor": api_result["cursor"],
            "results": final_results}


@tool
@handle_exceptions
def get_wallet_stats(wallet_address: str, output_include: list[str]) -> dict:
    """
    Get the stats for a wallet address.

    Args:
        wallet_address (str): Ethereum wallet address

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - nfts, collections, transactions, nft_transfers, token_transfers
    """
    params = {
        "chain": "eth",
        "address": wallet_address
    }

    result = evm_api.wallets.get_wallet_stats(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return {item: result[item]
            for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_wallet_history(wallet_address: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers
    and contract interactions. (paginated & in descending order)

    Args:
        wallet_address (str): Ethereum wallet address
        output_include (list[str]): A list of field names to include in the output.
        cursor (str): The cursor returned in the previous response (used for getting the next page). end of page cursor is None

    Returns:
        dict[str, Any]:
            A dictionary where each key-value pair only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - hash, from_address_entity, from_address_entity_logo, from_address,
              from_address_label, to_address_entity, to_address_entity_logo, to_address, to_address_label,
              value, receipt_contract_address, block_timestamp, block_number, block_hash, internal_transactions,
              nft_transfers, erc20_transfer, native_transfers
    """
    params = {
        "chain": "eth",
        "order": "DESC",
        "address": wallet_address
    }

    if cursor:
        params["cursor"] = cursor

    api_result = evm_api.wallets.get_wallet_history(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    final_results = []
    for result in api_result["result"]:
        final_results.append({item: result[item]
                              for item in result.keys() if item in output_include})

    return {"cursor": api_result["cursor"],
            "results": final_results}


@tool
@handle_exceptions
def get_transaction_detail(transaction_hash: str, output_include: list[str]) -> dict:
    """
    Get the contents of a transaction by the given transaction hash.

    Args:
        transaction_hash (str): transaction hash to be decoded
        output_include (list[str]): A list of field names to include in the output.

    Returns:
        dict[str, Any]:
            A dictionary where each key-value pair only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - hash, from_address_entity, from_address_entity_logo, from_address,
              from_address_label, to_address_entity, to_address_entity_logo, to_address, to_address_label,
              value, receipt_gas_used, receipt_contract_address, receipt_root, receipt_status, block_timestamp,
              block_number, block_hash, decoded_call, decoded_event


    """
    params = {
        "chain": "eth",
        "transaction_hash": transaction_hash
    }

    result = evm_api.transaction.get_transaction_verbose(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return {item: result[item]
            for item in result.keys() if item in output_include}


@tool
@handle_exceptions
def get_token_approvals(wallet_address: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Get ERC20 approvals for one or many wallet addresses and/or contract addresses, ordered by block number in descending order.

    Args:
        wallet_address (str): Ethereum wallet address
        output_include (list[str]): A list of field names to include in the output.
        cursor (str): The cursor returned in the previous response (used for getting the next page). end of page cursor is None

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - block_number, block_timestamp, transaction_hash, value, value_formatted, token, spender
    """
    base_url = _MORALIS_URL
    api_url = f"{base_url}/wallets/{wallet_address}/approvals"

    params = {'chain': 'eth'}

    if cursor:
        params["cursor"] = cursor

    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get token approvals. Status code: {response.status_code}")

    api_result = response.json()

    results = api_result["result"]
    final_results = []
    for result in results:
        final_results.append({item: result[item]
                              for item in result.keys() if item in output_include})

    return {"cursor": api_result["cursor"],
            "results": final_results}
