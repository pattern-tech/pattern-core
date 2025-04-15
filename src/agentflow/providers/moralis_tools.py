"""
MORALIS API v2.2
"""
import requests

from moralis import evm_api
from langchain.tools import tool

from src.util.configuration import Config
from src.util.exceptions import NotSupportedError
from src.agentflow.utils.shared_tools import handle_exceptions

_config = Config.get_config()
_moralis_config = Config.get_service_config(_config, "MORALIS")

_MORALIS_URL = "https://deep-index.moralis.io/api/v2.2"


def check_chain_supported(chain: str) -> bool:
    """
    Moralis supported chains in v2.2
    """
    supported_chains = ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38",
                        "gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
    if chain in supported_chains:
        return True
    raise NotSupportedError(
        f"chain {chain} is not supported. supported chains are : {supported_chains}")


@tool
@handle_exceptions
def get_wallet_token_balances(wallet_address: str, chain: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Get token balances for a specific wallet address in a specific chian. (paginated)
    apply decimal conversion for balance

    Args:
        wallet_address (str):  Wallet address
        chain (str): The chain ID can be ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38","gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
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
    check_chain_supported(chain)

    params = {
        "chain": chain,
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

    return {"cursor": api_result.get("cursor",None),
            "results": final_results}


@tool
@handle_exceptions
def get_wallet_stats(wallet_address: str, chain: str, output_include: list[str]) -> dict:
    """
    Get the stats for a wallet address in a specific chain.

    Args:
        wallet_address (str):  Wallet address
        chain (str): The chain ID can be ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38","gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
        output_include (list[str]): A list of field names to include in the output.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - nfts, collections, transactions, nft_transfers, token_transfers
    """
    check_chain_supported(chain)

    params = {
        "chain": chain,
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
def get_wallet_transactions(wallet_address: str, chain: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers
    and contract interactions in a specific chain. (paginated & in descending order)

    Args:
        wallet_address (str):  Wallet address
        chain (str): The chain ID can be ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38","gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
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
    check_chain_supported(chain)

    params = {
        "chain": chain,
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

    return {"cursor": api_result.get("cursor", None),
            "results": final_results}


@tool
@handle_exceptions
def get_transaction_detail(transaction_hash: str, chain: str, output_include: list[str]) -> dict:
    """
    Get the contents of a transaction for a specific chain by the given transaction hash.

    Args:
        transaction_hash (str): transaction hash to be decoded
        chain (str): The chain ID can be ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38","gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
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
    check_chain_supported(chain)

    params = {
        "chain": chain,
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
def get_token_approvals(wallet_address: str, chain: str, output_include: list[str], cursor: str = "") -> dict:
    """
    Get ERC20 approvals for one or many wallet addresses for a specific chain and/or contract addresses, ordered by block number in descending order.

    Args:
        wallet_address (str):  Wallet address
        chain (str): The chain ID can be ["eth", "0x1", "polygon", "0x89", "bsc", "0x38", "avalanche", "0xa86a", "fantom", "0xfa", "palm", "0x2a15c308d", "cronos", "0x19", "arbitrum", "0xa4b1", "chiliz", "0x15b38","gnosis", "0x64", "base", "0x2105", "optimism", "0xa", "linea", "0xe708", "moonbeam", "0x504", "moonriver", "0x505", "flow", "0x2eb", "ronin", "0x7e4", "lisk", "0x46f", "pulse", "0x171"]
        output_include (list[str]): A list of field names to include in the output.
        cursor (str): The cursor returned in the previous response (used for getting the next page). end of page cursor is None

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - block_number, block_timestamp, transaction_hash, value, value_formatted, token, spender
    """
    check_chain_supported(chain)

    base_url = _MORALIS_URL
    api_url = f"{base_url}/wallets/{wallet_address}/approvals"

    params = {'chain': chain}

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

    return {"cursor": api_result.get("cursor", None),
            "results": final_results}
