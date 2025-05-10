import os
import requests

from typing import Dict, Any, List, Optional
from langchain.tools import tool

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions


# Base URL for the Ergo Explorer API
ERGO_API_BASE_URL = "https://api.ergoplatform.com"


def _make_request(endpoint: str, params: Dict = None) -> Dict[str, Any]:
    """
    Make a request to the Ergo API.

    Args:
        endpoint: API endpoint to call
        params: Optional parameters for the request

    Returns:
        Dict: API response data
    """
    url = f"{ERGO_API_BASE_URL}{endpoint}"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


# === TRANSACTIONS METHODS ===

@tool
@handle_exceptions
def get_transaction(tx_id: str) -> Dict[str, Any]:
    """
    Get Ergo transaction details by transaction ID.

    Args:
        tx_id (str): Transaction ID

    Returns:
        Dict[str, Any]: Ergo transaction details
    """
    endpoint = f"/api/v1/transactions/{tx_id}"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_transactions_by_inputs_script_template_hash(hash: str, offset: int = 0, limit: int = 100, sort_direction: str = "desc") -> Dict[str, Any]:
    """
    Get Ergo transactions by inputs script template hash.

    Args:
        hash (str): Script template hash
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_direction (str): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of Ergo transactions
    """
    endpoint = f"/api/v1/transactions/byInputsScriptTemplateHash/{hash}"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_transactions_by_global_index(min_gix: int, limit: int) -> Dict[str, Any]:
    """
    Get a stream of Ergo transactions ordered by global index.

    Args:
        min_gix (int): Minimum global index
        limit (int): Maximum number of items to retrieve (max 500)

    Returns:
        Dict[str, Any]: List of Ergo transactions
    """
    endpoint = "/api/v1/transactions/byGlobalIndex/stream"
    params = {
        "minGix": min_gix,
        "limit": limit
    }
    return _make_request(endpoint, params)


# === BOXES METHODS ===

@tool
@handle_exceptions
def get_box(box_id: str) -> Dict[str, Any]:
    """
    Get Ergo box details by box ID.

    Args:
        box_id (str): Box ID

    Returns:
        Dict[str, Any]: Ergo box details with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/{box_id}"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_unspent_boxes_by_last_epochs(last_epochs: int) -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by last epochs.

    Args:
        last_epochs (int): Number of last epochs (max 1536)

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = "/api/v1/boxes/unspent/byLastEpochs/stream"
    params = {
        "lastEpochs": last_epochs
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_global_index(min_gix: int, limit: int) -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by global index.

    Args:
        min_gix (int): Minimum global index
        limit (int): Maximum number of items to retrieve (max 500)

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = "/api/v1/boxes/unspent/byGlobalIndex/stream"
    params = {
        "minGix": min_gix,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_stream(min_height: int, max_height: int) -> Dict[str, Any]:
    """
    Get a stream of unspent Ergo boxes.

    Args:
        min_height (int): Minimum block height
        max_height (int): Maximum block height

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = "/api/v1/boxes/unspent/stream"
    params = {
        "minHeight": min_height,
        "maxHeight": max_height
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_boxes_by_ergo_tree_template_hash_stream(hash: str, min_height: int, max_height: int) -> Dict[str, Any]:
    """
    Get Ergo boxes by ErgoTree template hash as a stream.

    Args:
        hash (str): ErgoTree template hash
        min_height (int): Minimum block height
        max_height (int): Maximum block height

    Returns:
        Dict[str, Any]: List of Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/byErgoTreeTemplateHash/{hash}/stream"
    params = {
        "minHeight": min_height,
        "maxHeight": max_height
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_ergo_tree_template_hash_stream(hash: str, min_height: int, max_height: int) -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by ErgoTree template hash as a stream.

    Args:
        hash (str): ErgoTree template hash
        min_height (int): Minimum block height
        max_height (int): Maximum block height

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/byErgoTreeTemplateHash/{hash}/stream"
    params = {
        "minHeight": min_height,
        "maxHeight": max_height
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 50, sort_direction: str = "desc") -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by token ID.

    Args:
        token_id (str): Token ID
        offset (int): Pagination offset
        limit (int): Number of items per page (max 100)
        sort_direction (str): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes containing the token with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/byTokenId/{token_id}"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_boxes_by_token_id(token_id: str, offset: int = 0, limit: int = 50) -> Dict[str, Any]:
    """
    Get Ergo boxes by token ID.

    Args:
        token_id (str): Token ID
        offset (int): Pagination offset
        limit (int): Number of items per page (max 100)

    Returns:
        Dict[str, Any]: List of Ergo boxes containing the token with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/byTokenId/{token_id}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_boxes_by_ergo_tree(ergo_tree: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get Ergo boxes by ErgoTree.

    Args:
        ergo_tree (str): Hex-encoded ErgoTree
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/byErgoTree/{ergo_tree}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_boxes_by_ergo_tree_template_hash(hash: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get Ergo boxes by ErgoTree template hash.

    Args:
        hash (str): ErgoTree template hash
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/byErgoTreeTemplateHash/{hash}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_ergo_tree(ergo_tree: str, offset: int = 0, limit: int = 100, sort_direction: str = "desc") -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by ErgoTree.

    Args:
        ergo_tree (str): Hex-encoded ErgoTree
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_direction (str): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/byErgoTree/{ergo_tree}"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_ergo_tree_template_hash(hash: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by ErgoTree template hash.

    Args:
        hash (str): ErgoTree template hash
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/byErgoTreeTemplateHash/{hash}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_boxes_by_address(address: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Get Ergo boxes by address.

    Args:
        address (str): Ergo blockchain address
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/byAddress/{address}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unconfirmed_unspent_boxes_by_address(address: str, sort_direction: str = "desc") -> Dict[str, Any]:
    """
    Get unconfirmed unspent Ergo boxes by address.

    Args:
        address (str): Ergo blockchain address
        sort_direction (str): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of unconfirmed unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/unconfirmed/byAddress/{address}"
    params = {
        "sortDirection": sort_direction
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_unspent_boxes_by_address(address: str, offset: int = 0, limit: int = 100, sort_direction: str = "desc") -> Dict[str, Any]:
    """
    Get unspent Ergo boxes by address.

    Args:
        address (str): Ergo blockchain address
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_direction (str): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes with Erg token values using 9 decimal places
    """
    endpoint = f"/api/v1/boxes/unspent/byAddress/{address}"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction
    }
    return _make_request(endpoint, params)


# === TOKENS/ASSETS METHODS ===

@tool
@handle_exceptions
def get_tokens(offset: int = 0, limit: int = 100, sort_direction: str = "desc", hide_nfts: bool = False) -> Dict[str, Any]:
    """
    Get all Ergo tokens/assets.

    Args:
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_direction (str): Sort direction, "asc" or "desc"
        hide_nfts (bool): Whether to exclude NFTs from results

    Returns:
        Dict[str, Any]: List of Ergo tokens with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = "/api/v1/tokens"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction,
        "hideNfts": hide_nfts
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def search_tokens(query: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Search for Ergo tokens by ID or Symbol.

    Args:
        query (str): Search query (min 3 characters)
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of matching Ergo tokens with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = "/api/v1/tokens/search"
    params = {
        "query": query,
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_tokens_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Get Ergo tokens by symbol.

    Args:
        symbol (str): Token symbol

    Returns:
        Dict[str, Any]: List of Ergo tokens with the given symbol with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = f"/api/v1/tokens/bySymbol/{symbol}"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_token(token_id: str) -> Dict[str, Any]:
    """
    Get Ergo token details by token ID.

    Args:
        token_id (str): Token ID

    Returns:
        Dict[str, Any]: Ergo token details with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = f"/api/v1/tokens/{token_id}"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_assets(offset: int = 0, limit: int = 100, sort_direction: str = "desc", hide_nfts: bool = False) -> Dict[str, Any]:
    """
    Get all Ergo assets (deprecated, use get_tokens instead).

    Args:
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_direction (str): Sort direction, "asc" or "desc"
        hide_nfts (bool): Whether to exclude NFTs from results

    Returns:
        Dict[str, Any]: List of Ergo assets with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = "/api/v1/assets"
    params = {
        "offset": offset,
        "limit": limit,
        "sortDirection": sort_direction,
        "hideNfts": hide_nfts
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def search_assets_by_token_id(query: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
    """
    Search for Ergo assets by token ID.

    Args:
        query (str): Search query (min 5 characters)
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)

    Returns:
        Dict[str, Any]: List of matching Ergo assets with decimal places (typically 9 for Ergo tokens)
    """
    endpoint = "/api/v1/assets/search/byTokenId"
    params = {
        "query": query,
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


# === EPOCHS METHODS ===

@tool
@handle_exceptions
def get_epochs_params() -> Dict[str, Any]:
    """
    Get parameters for current Ergo epoch.

    Returns:
        Dict[str, Any]: Current Ergo epoch parameters
    """
    endpoint = "/api/v1/epochs/params"
    return _make_request(endpoint)


# === ADDRESSES METHODS ===

@tool
@handle_exceptions
def get_address_transactions(
    address: str,
    offset: int = 0,
    limit: int = 100,
    concise: bool = False,
    from_height: Optional[int] = None,
    to_height: Optional[int] = None
) -> Dict[str, Any]:
    """
    Get Ergo transactions for a specific address.

    Args:
        address (str): Ergo blockchain address
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        concise (bool): Display only address inputs/outputs in transaction
        from_height (int, optional): Minimum block height
        to_height (int, optional): Maximum block height

    Returns:
        Dict[str, Any]: List of Ergo transactions for the address with token values using 9 decimal places
    """
    endpoint = f"/api/v1/addresses/{address}/transactions"
    params = {
        "offset": offset,
        "limit": limit,
        "concise": concise
    }
    if from_height is not None:
        params["fromHeight"] = from_height
    if to_height is not None:
        params["toHeight"] = to_height

    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_address_balance_confirmed(address: str, min_confirmations: Optional[int] = None) -> Dict[str, Any]:
    """
    Get confirmed Ergo balance for a specific address.

    Args:
        address (str): Ergo blockchain address
        min_confirmations (int, optional): Minimum number of confirmations

    Returns:
        Dict[str, Any]: Confirmed Ergo balance for the address with token values using 9 decimal places
    """
    endpoint = f"/api/v1/addresses/{address}/balance/confirmed"
    params = {}
    if min_confirmations is not None:
        params["minConfirmations"] = min_confirmations

    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_address_balance_total(address: str) -> Dict[str, Any]:
    """
    Get total Ergo balance for a specific address.

    Args:
        address (str): Ergo blockchain address

    Returns:
        Dict[str, Any]: Total Ergo balance for the address including confirmed and unconfirmed with token values using 9 decimal places
    """
    endpoint = f"/api/v1/addresses/{address}/balance/total"
    return _make_request(endpoint)


# === BLOCKS METHODS ===

@tool
@handle_exceptions
def get_blocks(offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_direction: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Ergo blocks.

    Args:
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_by (str, optional): Field to sort by
        sort_direction (str, optional): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of Ergo blocks
    """
    endpoint = "/api/v1/blocks"
    params = {
        "offset": offset,
        "limit": limit
    }
    if sort_by:
        params["sortBy"] = sort_by
    if sort_direction:
        params["sortDirection"] = sort_direction

    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_block(block_id: str) -> Dict[str, Any]:
    """
    Get Ergo block details by block ID.

    Args:
        block_id (str): Block ID

    Returns:
        Dict[str, Any]: Ergo block details
    """
    endpoint = f"/api/v1/blocks/{block_id}"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_block_headers(offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, sort_direction: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Ergo block headers.

    Args:
        offset (int): Pagination offset
        limit (int): Number of items per page (max 500)
        sort_by (str, optional): Field to sort by
        sort_direction (str, optional): Sort direction, "asc" or "desc"

    Returns:
        Dict[str, Any]: List of Ergo block headers
    """
    endpoint = "/api/v1/blocks/headers"
    params = {
        "offset": offset,
        "limit": limit
    }
    if sort_by:
        params["sortBy"] = sort_by
    if sort_direction:
        params["sortDirection"] = sort_direction

    return _make_request(endpoint, params)


# === MEMPOOL METHODS ===

@tool
@handle_exceptions
def get_mempool_transactions_by_address(address: str, offset: int = 0, limit: int = 50) -> Dict[str, Any]:
    """
    Get Ergo mempool transactions for a specific address.

    Args:
        address (str): Ergo blockchain address
        offset (int): Pagination offset
        limit (int): Number of items per page

    Returns:
        Dict[str, Any]: List of Ergo mempool transactions for the address
    """
    endpoint = f"/api/v1/mempool/transactions/byAddress/{address}"
    params = {
        "offset": offset,
        "limit": limit
    }
    return _make_request(endpoint, params)


@tool
@handle_exceptions
def get_mempool_unspent_boxes() -> Dict[str, Any]:
    """
    Get a stream of unspent Ergo outputs from mempool.

    Returns:
        Dict[str, Any]: List of unspent Ergo boxes in mempool
    """
    endpoint = "/api/v1/mempool/boxes/unspent"
    return _make_request(endpoint)


# === INFO METHODS ===

@tool
@handle_exceptions
def get_info() -> Dict[str, Any]:
    """
    Get basic information about the Ergo blockchain (deprecated).

    Returns:
        Dict[str, Any]: Basic Ergo blockchain info
    """
    endpoint = "/api/v1/info"
    return _make_request(endpoint)


@tool
@handle_exceptions
def get_network_state() -> Dict[str, Any]:
    """
    Get current Ergo network state.

    Returns:
        Dict[str, Any]: Current state of the Ergo network
    """
    endpoint = "/api/v1/networkState"
    return _make_request(endpoint)
