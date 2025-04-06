import requests

from typing import Any
from moralis import evm_api
from src.agentflow.utils.shared_tools import tool

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions
from src.agentflow.models.moralis_models import (
    TokenBalanceResponse,
    TokenBalanceInput,
    WalletHistoryInput,
    WalletHistoryResponse,
    WalletStatsInput,
    WalletStatsResponse,
    TransactionDetailInput,
    TransactionDetailResponse,
    TokenApprovalInput,
    TokenApprovalResponse)

_config = Config.get_config()
_moralis_config = Config.get_service_config(_config, "MORALIS")

_MORALIS_URL = "https://deep-index.moralis.io/api/v2"


@tool
@handle_exceptions
def get_wallet_token_balances(input_data: TokenBalanceInput) -> TokenBalanceResponse:
    """
    Get token balances for a specific wallet address and their token prices in USD (paginated).
    Apply decimal conversion for balance.

    Args:
        input_data: Input parameters including wallet address and various query options. Can be either a TokenBalanceInput model or a dictionary.

    Returns:
        TokenBalanceResponse: A response object containing the wallet token balances with prices
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = TokenBalanceInput(**input_data)
    else:
        input_model = input_data

    # Start with required parameters
    params = {
        "address": input_model.wallet_address,
        "chain": input_model.chain
    }

    # Add optional parameters if provided
    if input_model.cursor:
        params["cursor"] = input_model.cursor

    if input_model.token_addresses:
        params["token_addresses"] = input_model.token_addresses

    if input_model.exclude_spam is not None:
        params["exclude_spam"] = input_model.exclude_spam

    if input_model.exclude_native is not None:
        params["exclude_native"] = input_model.exclude_native

    if input_model.limit is not None:
        params["limit"] = input_model.limit

    api_result = evm_api.wallets.get_wallet_token_balances_price(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return api_result


@tool
@handle_exceptions
def get_wallet_stats(input_data: WalletStatsInput) -> WalletStatsResponse:
    """
    Get the stats for a wallet address, including NFT counts, transaction counts, and transfer counts.

    Args:
        input_data: Input parameters including wallet address and chain. Can be either a WalletStatsInput model or a dictionary.

    Returns:
        WalletStatsResponse: A response object containing wallet statistics
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = WalletStatsInput(**input_data)
    else:
        input_model = input_data

    # Prepare parameters for the API call
    params = {
        "chain": input_model.chain,
        "address": input_model.wallet_address
    }

    # Call the Moralis API
    api_result = evm_api.wallets.get_wallet_stats(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return api_result


@tool
@handle_exceptions
def get_wallet_history(input_data: WalletHistoryInput) -> WalletHistoryResponse:
    """
    Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers
    and contract interactions. (paginated & in descending order)

    Args:
        input_data: Input parameters including wallet address and various query options. Can be either a WalletHistoryInput model or a dictionary.

    Returns:
        WalletHistoryResponse: A response object containing the wallet transaction history
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = WalletHistoryInput(**input_data)
    else:
        input_model = input_data

    # Start with required parameters
    params = {
        "address": input_model.wallet_address,
        "chain": input_model.chain,
        "order": input_model.order
    }

    # Add optional parameters if provided
    if input_model.cursor:
        params["cursor"] = input_model.cursor

    if input_model.from_block is not None:
        params["from_block"] = input_model.from_block

    if input_model.to_block is not None:
        params["to_block"] = input_model.to_block

    if input_model.from_date:
        params["from_date"] = input_model.from_date

    if input_model.to_date:
        params["to_date"] = input_model.to_date

    if input_model.limit is not None:
        params["limit"] = input_model.limit

    api_result = evm_api.wallets.get_wallet_history(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return api_result


@tool
@handle_exceptions
def get_transaction_detail(input_data: TransactionDetailInput) -> TransactionDetailResponse:
    """
    Get the contents of a transaction by the given transaction hash.

    Args:
        input_data: Input parameters including transaction hash and chain. Can be either a TransactionDetailInput model or a dictionary.

    Returns:
        TransactionDetailResponse: A response object containing the transaction details
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = TransactionDetailInput(**input_data)
    else:
        input_model = input_data

    # Prepare parameters for the API call
    params = {
        "chain": input_model.chain,
        "transaction_hash": input_model.transaction_hash
    }

    # Add optional parameters if provided
    if input_model.include:
        params["include"] = input_model.include

    # Call the Moralis API
    api_result = evm_api.transaction.get_transaction_verbose(
        api_key=_moralis_config["api_key"],
        params=params,
    )

    return api_result


@tool
@handle_exceptions
def get_token_approvals(input_data: TokenApprovalInput) -> TokenApprovalResponse:
    """
    Get ERC20 approvals for a wallet address, ordered by block number in descending order.

    Args:
        input_data: Input parameters including wallet address, chain, and pagination options. Can be either a TokenApprovalInput model or a dictionary.

    Returns:
        TokenApprovalResponse: A response object containing the token approvals
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = TokenApprovalInput(**input_data)
    else:
        input_model = input_data

    # Prepare the API URL and parameters
    base_url = _MORALIS_URL
    api_url = f"{base_url}/wallets/{input_model.wallet_address}/approvals"

    params = {'chain': input_model.chain}

    # Add optional parameters if provided
    if input_model.cursor:
        params["cursor"] = input_model.cursor

    if input_model.limit is not None:
        params["limit"] = input_model.limit

    # Set up headers
    headers = {
        'accept': 'application/json',
        'X-API-Key': _moralis_config["api_key"]
    }

    # Make the API request
    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(
            f"Failed to get token approvals. Status code: {response.status_code}")

    # Parse the response
    api_result = response.json()

    # Convert to Pydantic model
    return TokenApprovalResponse(**api_result)
