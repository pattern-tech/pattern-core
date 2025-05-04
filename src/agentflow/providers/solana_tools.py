import os
import json
import time
import requests
from typing import Dict, List, Any, Optional

from langchain.tools import tool
from src.agentflow.utils.shared_tools import handle_exceptions
from src.util.configuration import Config


def _get_solscan_config() -> Dict:
    """
    Retrieve Solscan API configuration.

    Returns:
        Dict: Configuration dictionary with URL and API key.
    """
    _config = {}
    _config["URL"] = "https://pro-api.solscan.io/v2.0"
    _config["API_KEY"] = os.environ.get("SOLSCAN_API_KEY", "")

    if not _config["API_KEY"]:
        raise ValueError("SOLSCAN_API_KEY not found in environment variables")

    return _config


@tool
@handle_exceptions
def get_account_detail(address: str) -> Dict[str, Any]:
    """
    Get the details of a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.

    Returns:
        Dict[str, Any]: Account details information.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/detail"
    headers = {"accept": "application/json", "token": config['API_KEY']}
    params = {"address": address}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "account_detail": result
    }


@tool
@handle_exceptions
def get_account_transfer(
    address: str,
    activity_type: Optional[List[str]] = None,
    token_account: Optional[str] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    token: Optional[str] = None,
    amount: Optional[List[float]] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    exclude_amount_zero: Optional[bool] = None,
    flow: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "block_time",
    sort_order: str = "desc",
    value: Optional[List[float]] = None,
    block_time: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Get transfer data of a Solana account.

    Args:
        address (str): Solana wallet address.
        activity_type (Optional[List[str]]): Type of transfer. Can be: ["ACTIVITY_SPL_TRANSFER", "ACTIVITY_SPL_BURN", "ACTIVITY_SPL_MINT", "ACTIVITY_SPL_CREATE_ACCOUNT"].
        token_account (Optional[str]): Filter transfers for a specific token account in the wallet.
        from_address (Optional[str]): Filter transfer data with direction is from an address.
        to_address (Optional[str]): Filter transfers from a specific address.
        token (Optional[str]): Filter by token address. For native SOL transfers, use So11111111111111111111111111111111111111111.
        amount (Optional[List[float]]): Filter by amount range for a specific token. Example: [1, 2]
        from_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        to_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        exclude_amount_zero (Optional[bool]): Exclude transfers with zero amount.
        flow (Optional[str]): Filter by transfer direction: 'in' or 'out'.
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        sort_by (str): The field to sort by. Default is "block_time".
        sort_order (str): The sort order. Default is "desc".
        value (Optional[List[float]]): Filter by value range (dollar). Example: [1, 10]
        block_time (Optional[List[int]]): Filter by block time range (Unix timestamp in seconds). Example: [1720153259, 1720153276]

    Returns:
        Dict[str, Any]: Transfer data for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/transfer"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    # Add optional parameters if provided
    if activity_type:
        params["activity_type"] = activity_type
    if token_account:
        params["token_account"] = token_account
    if from_address:
        params["from"] = from_address
    if to_address:
        params["to"] = to_address
    if token:
        params["token"] = token
    if amount:
        params["amount[]"] = amount
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if exclude_amount_zero is not None:
        params["exclude_amount_zero"] = exclude_amount_zero
    if flow:
        params["flow"] = flow
    if value:
        params["value[]"] = value
    if block_time:
        params["block_time[]"] = block_time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "transfers": result
    }


@tool
@handle_exceptions
def get_account_defi_activities(
    address: str,
    activity_type: Optional[List[str]] = None,
    from_address: Optional[str] = None,
    platform: Optional[List[str]] = None,
    source: Optional[List[str]] = None,
    token: Optional[str] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "block_time",
    sort_order: str = "desc",
    block_time: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Get DeFi activities involving a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.
        activity_type (Optional[List[str]]): Type of activity data. Can be: ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP", "ACTIVITY_TOKEN_ADD_LIQ", "ACTIVITY_TOKEN_REMOVE_LIQ", "ACTIVITY_SPL_TOKEN_STAKE", "ACTIVITY_SPL_TOKEN_UNSTAKE", "ACTIVITY_TOKEN_DEPOSIT_VAULT", "ACTIVITY_TOKEN_WITHDRAW_VAULT", "ACTIVITY_SPL_INIT_MINT", "ACTIVITY_ORDERBOOK_ORDER_PLACE"].
        from_address (Optional[str]): Filter activities from an address.
        platform (Optional[List[str]]): Filter by list platform addresses. Maximum 5 addresses.
        source (Optional[List[str]]): Filter by list source addresses. Maximum 5 addresses.
        token (Optional[str]): Filter activities data by token address.
        from_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        to_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        sort_by (str): The field to sort by. Default is "block_time".
        sort_order (str): The sort order. Default is "desc".
        block_time (Optional[List[int]]): Used when you want to filter data by block time. Format time: UnixTime in seconds. Example: [1720153259, 1720153276]

    Returns:
        Dict[str, Any]: DeFi activities for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/defi/activities"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    # Add optional parameters if provided
    if activity_type:
        params["activity_type"] = activity_type
    if from_address:
        params["from"] = from_address
    if platform:
        params["platform"] = platform
    if source:
        params["source"] = source
    if token:
        params["token"] = token
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if block_time:
        params["block_time[]"] = block_time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "defi_activities": result
    }


@tool
@handle_exceptions
def get_account_balance_change(
    address: str,
    token_account: Optional[str] = None,
    token: Optional[str] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    page_size: int = 10,
    page: int = 1,
    remove_spam: Optional[str] = None,
    amount: Optional[List[float]] = None,
    flow: Optional[str] = None,
    sort_by: str = "block_time",
    sort_order: str = "desc",
    block_time: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Get balance change activities involving a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.
        token_account (Optional[str]): A token account of wallet on Solana blockchain.
        token (Optional[str]): Filter activities data by token address.
        from_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        to_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        page (int): Page number for pagination. Default is 1.
        remove_spam (Optional[str]): The query parameter to determine if spam activities have been removed or not.
        amount (Optional[List[float]]): Filter by amount range for a specific token. Example: [1, 2]
        flow (Optional[str]): Filter by change direction: 'in' or 'out'.
        sort_by (str): The field to sort by. Default is "block_time".
        sort_order (str): The sort order. Default is "desc".
        block_time (Optional[List[int]]): Filter by block time range (Unix timestamp in seconds). Example: [1720153259, 1720153276]

    Returns:
        Dict[str, Any]: Balance change activities for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/balance_change"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page_size": page_size,
        "page": page,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    # Add optional parameters if provided
    if token_account:
        params["token_account"] = token_account
    if token:
        params["token"] = token
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if remove_spam:
        params["remove_spam"] = remove_spam
    if amount:
        params["amount[]"] = amount
    if flow:
        params["flow"] = flow
    if block_time:
        params["block_time[]"] = block_time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "balance_changes": result
    }


@tool
@handle_exceptions
def get_account_transactions(
    address: str,
    before: Optional[str] = None,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get the list of transactions of a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.
        before (Optional[str]): The signature of the latest transaction of previous page.
        limit (int): The number of transactions should be returned (10, 20, 30, or 40). Default is 10.

    Returns:
        Dict[str, Any]: List of transactions for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/transactions"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "limit": limit
    }

    if before:
        params["before"] = before

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "transactions": result
    }


@tool
@handle_exceptions
def get_account_portfolio(address: str) -> Dict[str, Any]:
    """
    Get the portfolio for a given Solana address.

    Args:
        address (str): A wallet address on Solana blockchain.

    Returns:
        Dict[str, Any]: Portfolio for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/portfolio"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "portfolio": result
    }


@tool
@handle_exceptions
def get_account_token_accounts(
    address: str,
    type: str,
    page: int = 1,
    page_size: int = 10,
    hide_zero: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Get token accounts of a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.
        type (str): Type of token, either "token" or "nft".
        page (int): Page number for pagination. Default is 1.
        page_size (int): The number of items per page (10, 20, 30, or 40). Default is 10.
        hide_zero (Optional[bool]): Filter tokens that have amount is zero.

    Returns:
        Dict[str, Any]: Token accounts for the address.
    """
    if type not in ["token", "nft"]:
        return {
            "success": False,
            "error": "Type must be either 'token' or 'nft'."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/account/token-accounts"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "type": type,
        "page": page,
        "page_size": page_size
    }

    if hide_zero is not None:
        params["hide_zero"] = hide_zero

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_accounts": result
    }


@tool
@handle_exceptions
def get_account_stake(
    address: str,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get the list of stake accounts of a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.
        page (int): Page number for pagination. Default is 1.
        page_size (int): The number of items per page (10, 20, 30, or 40). Default is 10.

    Returns:
        Dict[str, Any]: Stake accounts for the address.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/stake"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "stake_accounts": result
    }


@tool
@handle_exceptions
def get_account_metadata(address: str) -> Dict[str, Any]:
    """
    Get the metadata of a Solana account.

    Args:
        address (str): A wallet address on Solana blockchain.

    Returns:
        Dict[str, Any]: Metadata for the account.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/account/metadata"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "metadata": result
    }


@tool
@handle_exceptions
def get_account_leaderboard(
    sort_by: str = "total_values",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get the Solana account leaderboard.

    Args:
        sort_by (str): The field to sort by. Options are: "sol_values", "stake_values", "token_values", "total_values". Default is "total_values".
        sort_order (str): The sort order. Options are: "asc", "desc". Default is "desc".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 20, 30, 40, 60, or 100). Default is 10.

    Returns:
        Dict[str, Any]: Account leaderboard information.
    """
    valid_sort_by = ["sol_values", "stake_values",
                     "token_values", "total_values"]
    if sort_by not in valid_sort_by:
        return {
            "success": False,
            "error": f"sort_by must be one of {valid_sort_by}."
        }

    valid_sort_order = ["asc", "desc"]
    if sort_order not in valid_sort_order:
        return {
            "success": False,
            "error": f"sort_order must be one of {valid_sort_order}."
        }

    valid_page_sizes = [10, 20, 30, 40, 60, 100]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/account/leaderboard"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "page_size": page_size
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "leaderboard": result
    }


@tool
@handle_exceptions
def get_token_transfer(
    address: str,
    activity_type: Optional[List[str]] = None,
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    amount: Optional[List[float]] = None,
    block_time: Optional[List[int]] = None,
    exclude_amount_zero: Optional[bool] = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "block_time",
    sort_order: str = "desc",
    value: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Get transfer data of a Solana token.

    Args:
        address (str): A token address on Solana blockchain.
        activity_type (Optional[List[str]]): Type of transfer data. Can be: ["ACTIVITY_SPL_TRANSFER", "ACTIVITY_SPL_BURN", "ACTIVITY_SPL_MINT", "ACTIVITY_SPL_CREATE_ACCOUNT"].
        from_address (Optional[str]): Filter transfer data with direction is from an address.
        to_address (Optional[str]): Filter transfer data with direction is to an address.
        amount (Optional[List[float]]): Filter by amount range for a specific token. Example: [1, 2]
        block_time (Optional[List[int]]): Filter by block time range (Unix timestamp in seconds). Example: [1720153259, 1720153276]
        exclude_amount_zero (Optional[bool]): Exclude transfers with zero amount.
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        sort_by (str): The field to sort by. Default is "block_time".
        sort_order (str): The sort order. Default is "desc".
        value (Optional[List[float]]): Filter by value range (dollar). Example: [1, 10]

    Returns:
        Dict[str, Any]: Transfer data for the token.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/transfer"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    # Add optional parameters if provided
    if activity_type:
        params["activity_type"] = activity_type
    if from_address:
        params["from"] = from_address
    if to_address:
        params["to"] = to_address
    if amount:
        params["amount[]"] = amount
    if block_time:
        params["block_time[]"] = block_time
    if exclude_amount_zero is not None:
        params["exclude_amount_zero"] = exclude_amount_zero
    if value:
        params["value[]"] = value

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_transfers": result
    }


@tool
@handle_exceptions
def get_token_defi_activities(
    address: str,
    activity_type: Optional[List[str]] = None,
    from_address: Optional[str] = None,
    platform: Optional[List[str]] = None,
    source: Optional[List[str]] = None,
    token: Optional[str] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "block_time",
    sort_order: str = "desc",
    block_time: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Get DeFi activities involving a token.

    Args:
        address (str): A token address on Solana blockchain.
        activity_type (Optional[List[str]]): Type of defi-activity data. Can be: ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP", "ACTIVITY_TOKEN_ADD_LIQ", "ACTIVITY_TOKEN_REMOVE_LIQ", "ACTIVITY_SPL_TOKEN_STAKE", "ACTIVITY_SPL_TOKEN_UNSTAKE", "ACTIVITY_TOKEN_DEPOSIT_VAULT", "ACTIVITY_TOKEN_WITHDRAW_VAULT", "ACTIVITY_SPL_INIT_MINT", "ACTIVITY_ORDERBOOK_ORDER_PLACE"].
        from_address (Optional[str]): Filter activities from an address.
        platform (Optional[List[str]]): Filter by list platform addresses. Maximum 5 addresses.
        source (Optional[List[str]]): Filter by list source addresses. Maximum 5 addresses.
        token (Optional[str]): Filter activities data by token address.
        from_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        to_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        sort_by (str): The field to sort by. Default is "block_time".
        sort_order (str): The sort order. Default is "desc".
        block_time (Optional[List[int]]): Filter by block time range (Unix timestamp in seconds). Example: [1720153259, 1720153276]

    Returns:
        Dict[str, Any]: DeFi activities for the token.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/defi/activities"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order,
    }

    # Add optional parameters if provided
    if activity_type:
        params["activity_type"] = activity_type
    if from_address:
        params["from"] = from_address
    if platform:
        params["platform"] = platform
    if source:
        params["source"] = source
    if token:
        params["token"] = token
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if block_time:
        params["block_time[]"] = block_time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_defi_activities": result
    }


@tool
@handle_exceptions
def get_token_markets(
    token: List[str],
    sort_by: Optional[str] = None,
    program: Optional[List[str]] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get token markets information.

    Args:
        token (List[str]): List of token pair addresses.
        sort_by (Optional[str]): The parameter to specify the field for sorting the returned list.
        program (Optional[List[str]]): Filter by list program addresses. Maximum 5 addresses.
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 20, 30, 40, 60, 100). Default is 10.

    Returns:
        Dict[str, Any]: Token markets information.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/markets"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "page": page,
        "page_size": page_size
    }

    for t in token:
        params[f"token[]"] = t

    if sort_by:
        params["sort_by"] = sort_by
    if program:
        params["program"] = program

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_markets": result
    }


@tool
@handle_exceptions
def get_token_meta(address: str) -> Dict[str, Any]:
    """
    Get the metadata of a token.

    Args:
        address (str): A token address on Solana blockchain.

    Returns:
        Dict[str, Any]: Metadata for the token.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/meta"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_metadata": result
    }


@tool
@handle_exceptions
def get_token_meta_multi(address: List[str]) -> Dict[str, Any]:
    """
    Get the metadata of multiple tokens. Max 20 token addresses.

    Args:
        address (List[str]): A list of token addresses on Solana blockchain.

    Returns:
        Dict[str, Any]: Metadata for multiple tokens.
    """
    if len(address) > 20:
        return {
            "success": False,
            "error": "Maximum 20 token addresses allowed."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/token/meta/multi"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {}
    for a in address:
        params[f"address[]"] = a

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "tokens_metadata": result
    }


@tool
@handle_exceptions
def get_token_price(
    address: str,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    time: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get price of a token.

    Args:
        address (str): A token address on Solana blockchain.
        from_time (Optional[int]): Start time in YYYYMMDD format.
        to_time (Optional[int]): End time in YYYYMMDD format.
        time (Optional[List[str]]): Time range in YYYYMMDD format. Example: ["20240701", "20240715"]

    Returns:
        Dict[str, Any]: Price information for the token.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/price"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if time:
        params["time[]"] = time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_price": result
    }


@tool
@handle_exceptions
def get_token_price_multi(
    address: List[str],
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    time: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Get the price of multiple tokens. Max 20 token addresses.

    Args:
        address (List[str]): A list of token addresses on Solana blockchain.
        from_time (Optional[int]): Start time in YYYYMMDD format.
        to_time (Optional[int]): End time in YYYYMMDD format.
        time (Optional[List[str]]): Time range in YYYYMMDD format. Example: ["20240701", "20240715"]

    Returns:
        Dict[str, Any]: Price information for multiple tokens.
    """
    if len(address) > 20:
        return {
            "success": False,
            "error": "Maximum 20 token addresses allowed."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/token/price/multi"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {}
    for a in address:
        params[f"address[]"] = a

    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if time:
        params["time[]"] = time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "tokens_price": result
    }


@tool
@handle_exceptions
def get_token_holders(
    address: str,
    page: int = 1,
    page_size: int = 10,
    from_amount: Optional[str] = None,
    to_amount: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the list of token holders.

    Args:
        address (str): A token address on Solana blockchain.
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 20, 30, or 40). Default is 10.
        from_amount (Optional[str]): Filter holders by minimum token holding amount in string format.
        to_amount (Optional[str]): Filter holders by maximum token holding amount in string format.

    Returns:
        Dict[str, Any]: List of token holders.
    """
    valid_page_sizes = [10, 20, 30, 40]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/token/holders"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "address": address,
        "page": page,
        "page_size": page_size
    }

    if from_amount:
        params["from_amount"] = from_amount
    if to_amount:
        params["to_amount"] = to_amount

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_holders": result
    }


@tool
@handle_exceptions
def get_token_list(
    sort_by: Optional[str] = None,
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get the list of tokens.

    Args:
        sort_by (Optional[str]): The field to sort by. Options are: "holder", "market_cap", "created_time".
        sort_order (str): The sort order. Options are: "asc", "desc". Default is "desc".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100

    Returns:
        Dict[str, Any]: List of tokens.
    """
    if sort_by and sort_by not in ["holder", "market_cap", "created_time"]:
        return {
            "success": False,
            "error": "sort_by must be one of ['holder', 'market_cap', 'created_time']."
        }

    valid_sort_order = ["asc", "desc"]
    if sort_order not in valid_sort_order:
        return {
            "success": False,
            "error": f"sort_order must be one of {valid_sort_order}."
        }

    valid_page_sizes = [10, 20, 30, 40, 60, 100]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/token/list"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "sort_order": sort_order,
        "page": page,
        "page_size": page_size
    }

    if sort_by:
        params["sort_by"] = sort_by

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "token_list": result
    }


@tool
@handle_exceptions
def get_token_top() -> Dict[str, Any]:
    """
    Get the list of top tokens.

    Returns:
        Dict[str, Any]: List of top tokens.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/top"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "top_tokens": result
    }


@tool
@handle_exceptions
def get_token_trending(limit: int = 10) -> Dict[str, Any]:
    """
    Get the list of trending tokens.

    Args:
        limit (int): Number of items to return. Default is 10.

    Returns:
        Dict[str, Any]: List of trending tokens.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/token/trending"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"limit": limit}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "trending_tokens": result
    }


@tool
@handle_exceptions
def get_new_nft(
    filter: str = "created_time",
    page: int = 1,
    page_size: int = 12
) -> Dict[str, Any]:
    """
    Get the list of new NFTs.

    Args:
        filter (str): Filter by 'created_time'. Default is "created_time".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (12, 24, 36). Default is 12.

    Returns:
        Dict[str, Any]: List of new NFTs.
    """
    if filter != "created_time":
        return {
            "success": False,
            "error": "filter must be 'created_time'."
        }

    valid_page_sizes = [12, 24, 36]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/nft/news"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "filter": filter,
        "page": page,
        "page_size": page_size
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "new_nfts": result
    }


@tool
@handle_exceptions
def get_nft_activities(
    from_address: Optional[str] = None,
    to_address: Optional[str] = None,
    source: Optional[List[str]] = None,
    activity_type: Optional[List[str]] = None,
    from_time: Optional[int] = None,
    to_time: Optional[int] = None,
    token: Optional[str] = None,
    collection: Optional[str] = None,
    currency_token: Optional[str] = None,
    price: Optional[List[float]] = None,
    page: int = 1,
    page_size: int = 10,
    block_time: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Get NFT activities.

    Args:
        from_address (Optional[str]): Filter by from address.
        to_address (Optional[str]): Filter by to address.
        source (Optional[List[str]]): Filter by list source addresses. Maximum 5 addresses.
        activity_type (Optional[List[str]]): Type of NFT activity data. Can be: ["ACTIVITY_NFT_SOLD", "ACTIVITY_NFT_LISTING", "ACTIVITY_NFT_BIDDING", "ACTIVITY_NFT_CANCEL_BID", "ACTIVITY_NFT_CANCEL_LIST", "ACTIVITY_NFT_REJECT_BID", "ACTIVITY_NFT_UPDATE_PRICE", "ACTIVITY_NFT_LIST_AUCTION"].
        from_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        to_time (Optional[int]): Filter by time range (Unix timestamp in seconds).
        token (Optional[str]): Filter activities data by token address.
        collection (Optional[str]): Filter by collection.
        currency_token (Optional[str]): Filter by currency token.
        price (Optional[List[float]]): Filter by price range. Example: [1, 2]
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10. can be : 10, 20, 30, 40, 60, 100
        block_time (Optional[List[int]]): Filter by block time range (Unix timestamp in seconds). Example: [1720153259, 1720153276]

    Returns:
        Dict[str, Any]: NFT activities.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/nft/activities"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "page": page,
        "page_size": page_size
    }

    # Add optional parameters if provided
    if from_address:
        params["from"] = from_address
    if to_address:
        params["to"] = to_address
    if source:
        params["source"] = source
    if activity_type:
        params["activity_type"] = activity_type
    if from_time:
        params["from_time"] = from_time
    if to_time:
        params["to_time"] = to_time
    if token:
        params["token"] = token
    if collection:
        params["collection"] = collection
    if currency_token:
        params["currency_token"] = currency_token
    if price:
        params["price[]"] = price
    if block_time:
        params["block_time[]"] = block_time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "nft_activities": result
    }


@tool
@handle_exceptions
def get_nft_collection_lists(
    range_days: int = 1,
    sort_order: str = "desc",
    sort_by: str = "volumes",
    page: int = 1,
    page_size: int = 10,
    collection: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the list of NFT collections.

    Args:
        range_days (int): Days range. Options are: 1, 7, 30. Default is 1.
        sort_order (str): The sort order. Options are: "asc", "desc". Default is "desc".
        sort_by (str): The field to sort by. Options are: "items", "floor_price", "volumes". Default is "volumes".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 18, 20, 30, 40). Default is 10.
        collection (Optional[str]): Collection ID. If not provided, will return all collections.

    Returns:
        Dict[str, Any]: List of NFT collections.
    """
    if range_days not in [1, 7, 30]:
        return {
            "success": False,
            "error": "range_days must be one of [1, 7, 30]."
        }

    valid_sort_order = ["asc", "desc"]
    if sort_order not in valid_sort_order:
        return {
            "success": False,
            "error": f"sort_order must be one of {valid_sort_order}."
        }

    valid_sort_by = ["items", "floor_price", "volumes"]
    if sort_by not in valid_sort_by:
        return {
            "success": False,
            "error": f"sort_by must be one of {valid_sort_by}."
        }

    valid_page_sizes = [10, 18, 20, 30, 40]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/nft/collection/lists"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "range": range_days,
        "sort_order": sort_order,
        "sort_by": sort_by,
        "page": page,
        "page_size": page_size
    }

    if collection:
        params["collection"] = collection

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "nft_collections": result
    }


@tool
@handle_exceptions
def get_nft_collection_items(
    collection: str,
    sort_by: str = "last_trade",
    page: int = 1,
    page_size: int = 12
) -> Dict[str, Any]:
    """
    Get the list of items of a NFT collection.

    Args:
        collection (str): Collection ID.
        sort_by (str): The field to sort by. Options are: "last_trade", "listing_price". Default is "last_trade".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (12, 24, 36). Default is 12.

    Returns:
        Dict[str, Any]: List of NFT collection items.
    """
    valid_sort_by = ["last_trade", "listing_price"]
    if sort_by not in valid_sort_by:
        return {
            "success": False,
            "error": f"sort_by must be one of {valid_sort_by}."
        }

    valid_page_sizes = [12, 24, 36]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/nft/collection/items"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "collection": collection,
        "sort_by": sort_by,
        "page": page,
        "page_size": page_size
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "collection_items": result
    }


@tool
@handle_exceptions
def get_transaction_last(limit: int = 10, filter: str = "exceptVote") -> Dict[str, Any]:
    """
    Get the list of the latest transactions.

    Args:
        limit (int): The number of transactions to return (10, 20, 30, 40, 60, 100). Default is 10.
        filter (str): The filter parameter for excluding vote transactions. Options are: "exceptVote", "all". Default is "exceptVote".

    Returns:
        Dict[str, Any]: List of latest transactions.
    """
    valid_limit_values = [10, 20, 30, 40, 60, 100]
    if limit not in valid_limit_values:
        return {
            "success": False,
            "error": f"limit must be one of {valid_limit_values}."
        }

    valid_filter_values = ["exceptVote", "all"]
    if filter not in valid_filter_values:
        return {
            "success": False,
            "error": f"filter must be one of {valid_filter_values}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/transaction/last"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "limit": limit,
        "filter": filter
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "latest_transactions": result
    }


@tool
@handle_exceptions
def get_transaction_detail(tx: str) -> Dict[str, Any]:
    """
    Get the detail of a transaction. Returns transaction data after parsed by Solscan Parser. 

    The data includes helpful information such as:
    - Token and SOL balance changes
    - IDL data
    - DeFi or transfer activities of each instruction

    Args:
        tx (str): Transaction address.

    Returns:
        Dict[str, Any]: Detailed transaction information.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/transaction/detail"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"tx": tx}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "transaction_detail": result
    }


@tool
@handle_exceptions
def get_transaction_actions(tx: str) -> Dict[str, Any]:
    """
    Get the actions of a transaction. Returns actions like: transfers, swap activities, NFT activities...

    Args:
        tx (str): Transaction address.

    Returns:
        Dict[str, Any]: Transaction actions.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/transaction/actions"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"tx": tx}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "transaction_actions": result
    }


@tool
@handle_exceptions
def get_block_last(limit: int = 10) -> Dict[str, Any]:
    """
    Get the list of the latest blocks.

    Args:
        limit (int): The number of blocks to return (10, 20, 30, 40, 60, 100). Default is 10.

    Returns:
        Dict[str, Any]: List of latest blocks.
    """
    valid_limit_values = [10, 20, 30, 40, 60, 100]
    if limit not in valid_limit_values:
        return {
            "success": False,
            "error": f"limit must be one of {valid_limit_values}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/block/last"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"limit": limit}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "latest_blocks": result
    }


@tool
@handle_exceptions
def get_block_transactions(
    block: int,
    page: int = 1,
    page_size: int = 10,
    exclude_vote: Optional[bool] = None,
    program: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get the list of transactions of a block.

    Args:
        block (int): The slot index of a block.
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number of items per page (10, 20, 30, 40, 60, 100). Default is 10.
        exclude_vote (Optional[bool]): Whether to exclude vote transactions from the results.
        program (Optional[str]): The program used to filter transactions that interact with it.

    Returns:
        Dict[str, Any]: List of block transactions.
    """
    valid_page_sizes = [10, 20, 30, 40, 60, 100]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/block/transactions"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "block": block,
        "page": page,
        "page_size": page_size
    }

    if exclude_vote is not None:
        params["exclude_vote"] = exclude_vote
    if program:
        params["program"] = program

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "block_transactions": result
    }


@tool
@handle_exceptions
def get_block_detail(block: int) -> Dict[str, Any]:
    """
    Get the details of a block.

    Args:
        block (int): The slot index of a block.

    Returns:
        Dict[str, Any]: Block details.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/block/detail"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"block": block}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "block_detail": result
    }


@tool
@handle_exceptions
def get_market_list(
    page: int = 1,
    page_size: int = 10,
    program: Optional[str] = None,
    token_address: Optional[str] = None,
    sort_by: str = "created_time",
    sort_order: str = "desc"
) -> Dict[str, Any]:
    """
    Get the list of pool markets.

    Args:
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 20, 30, 40, 60, 100). Default is 10.
        program (Optional[str]): Program owner address.
        token_address (Optional[str]): Token address involving.
        sort_by (str): The field to sort by. Options are: "created_time", "volumes_24h", "trades_24h". Default is "created_time".
        sort_order (str): The sort order. Options are: "asc", "desc". Default is "desc".

    Returns:
        Dict[str, Any]: List of pool markets.
    """
    valid_page_sizes = [10, 20, 30, 40, 60, 100]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    valid_sort_by = ["created_time", "volumes_24h", "trades_24h"]
    if sort_by not in valid_sort_by:
        return {
            "success": False,
            "error": f"sort_by must be one of {valid_sort_by}."
        }

    valid_sort_order = ["asc", "desc"]
    if sort_order not in valid_sort_order:
        return {
            "success": False,
            "error": f"sort_order must be one of {valid_sort_order}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/market/list"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "sort_order": sort_order
    }

    if program:
        params["program"] = program
    if token_address:
        params["token_address"] = token_address

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "market_list": result
    }


@tool
@handle_exceptions
def get_market_info(address: str) -> Dict[str, Any]:
    """
    Get token market info.

    Args:
        address (str): Market Id.

    Returns:
        Dict[str, Any]: Market information.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/market/info"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "market_info": result
    }


@tool
@handle_exceptions
def get_market_volume(address: str, time: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get token market volume.

    Args:
        address (str): Market Id.
        time (Optional[List[str]]): Time range in YYYYMMDD format. Example: ["20240701", "20240715"]

    Returns:
        Dict[str, Any]: Market volume information.
    """
    config = _get_solscan_config()
    url = f"{config['URL']}/market/volume"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {"address": address}

    if time:
        params["time[]"] = time

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "market_volume": result
    }


@tool
@handle_exceptions
def get_program_list(
    sort_by: str = "num_txs",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Get list of programs that were active in the last 90 days.

    Args:
        sort_by (str): The field to sort by. Options are: "num_txs", "num_txs_success", "interaction_volume", "success_rate", "active_users_24h". Default is "num_txs".
        sort_order (str): The sort order. Options are: "asc", "desc". Default is "desc".
        page (int): Page number for pagination. Default is 1.
        page_size (int): Number items per page (10, 20, 30, 40, 60, 100). Default is 10.

    Returns:
        Dict[str, Any]: List of active programs.
    """
    valid_sort_by = ["num_txs", "num_txs_success",
                     "interaction_volume", "success_rate", "active_users_24h"]
    if sort_by not in valid_sort_by:
        return {
            "success": False,
            "error": f"sort_by must be one of {valid_sort_by}."
        }

    valid_sort_order = ["asc", "desc"]
    if sort_order not in valid_sort_order:
        return {
            "success": False,
            "error": f"sort_order must be one of {valid_sort_order}."
        }

    valid_page_sizes = [10, 20, 30, 40, 60, 100]
    if page_size not in valid_page_sizes:
        return {
            "success": False,
            "error": f"page_size must be one of {valid_page_sizes}."
        }

    config = _get_solscan_config()
    url = f"{config['URL']}/program/list"
    headers = {"accept": "application/json", "token": config['API_KEY']}

    params = {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "page_size": page_size
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    result = response.json()
    return {
        "success": True,
        "program_list": result
    }
