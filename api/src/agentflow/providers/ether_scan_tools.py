import os
import json
import time
import requests
import dateparser

from web3 import Web3
from langchain.tools import tool
from typing import List, Any, Optional, Dict

from src.agentflow.utils.shared_tools import handle_exceptions


def _get_api_key() -> str:
    """
    Retrieve the API key from the environment.

    Returns:
        str: The API key.

    Raises:
        Exception: If the API key is not found.
    """
    api_key = os.getenv("ETHER_SCAN_API_KEY")
    if not api_key:
        raise Exception("No API key found for etherscan.")
    return api_key


@handle_exceptions
def fetch_contract_abi(contract_address: str, api_key: str) -> Dict:
    """
    Retrieve the ABI of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The decrypted Etherscan API key.

    Returns:
        Dict: A dictionary representing the contract ABI.
    """
    url = os.environ["ETHER_SCAN_URL"]
    params = {
        "chainid": "1",
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": _get_api_key()
    }
    response = requests.get(url, params=params)

    result = response.json().get("result")
    if result is None:
        raise Exception("No ABI found for the contract.")

    return json.loads(result)


@handle_exceptions
def fetch_contract_source_code(contract_address: str, api_key: str) -> str:
    """
    Retrieve the source code of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The decrypted Etherscan API key.

    Returns:
        str: The contract source code.
    """
    url = os.environ["ETHER_SCAN_URL"]
    params = {
        "chainid": "1",
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": _get_api_key()
    }
    response = requests.get(url, params=params)
    return response.json()["result"][0]["SourceCode"]


@handle_exceptions
def get_event_abi(abi: List[Dict], event_name: str) -> Optional[Dict]:
    """
    Retrieve the ABI entry for a specific event.

    Args:
        abi (List[Dict]): The list of ABI definitions.
        event_name (str): The name of the event.

    Returns:
        Optional[Dict]: The event's ABI dictionary if found; otherwise, None.
    """
    for item in abi:
        if item.get("type") == "event" and item.get("name") == event_name:
            return item
    return None


@handle_exceptions
def timestamp_to_block_number(timestamp: int, api_key: str) -> int:
    """
    Convert a given Unix timestamp to the nearest Ethereum block number.

    Args:
        timestamp (int): Unix timestamp.
        api_key (str): The decrypted Etherscan API key.

    Returns:
        int: The closest block number.
    """
    url = os.environ["ETHER_SCAN_URL"]
    params = {
        "chainid": "1",
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": _get_api_key()
    }
    response = requests.get(url, params=params)
    return int(response.json()["result"])


@tool
@handle_exceptions
def get_current_timestamp() -> int:
    """
    Get the current Unix timestamp.

    Returns:
        int: The current timestamp.
    """
    return int(time.time())


@tool
@handle_exceptions
def convert_to_timestamp(date_str: str) -> int:
    """
    Convert a natural language date string into a Unix timestamp.

    Args:
        date_str (str): A human-readable date (e.g., "one month ago", "12/3/2020").

    Returns:
        int: The Unix timestamp corresponding to the provided date.

    Raises:
        ValueError: If the date string cannot be parsed.
    """
    parsed_date = dateparser.parse(date_str)
    if parsed_date:
        return int(time.mktime(parsed_date.timetuple()))
    else:
        raise ValueError(f"Could not parse the date string: {date_str}")


@tool
@handle_exceptions
def get_contract_source_code(contract_address: str) -> str:
    """
    Retrieve the source code of a smart contract.

    Args:
        contract_address (str): The contract address.

    Returns:
        str: The contract source code.
    """
    api_key = _get_api_key()
    return fetch_contract_source_code(contract_address, api_key)


@tool
@handle_exceptions
def get_contract_abi(contract_address: str) -> Dict:
    """
    Retrieve the ABI of a smart contract.

    Args:
        contract_address (str): The contract address.

    Returns:
        Dict: The contract ABI.
    """
    api_key = _get_api_key()
    return fetch_contract_abi(contract_address, api_key)


@tool
@handle_exceptions
def get_abi_of_event(contract_address: str, event_name: str) -> Dict:
    """
    Retrieve the ABI of a specific event from a smart contract.

    Args:
        contract_address (str): The smart contract address.
        event_name (str): The name of the event.

    Returns:
        Dict: The ABI of the specified event.

    Raises:
        Exception: If the API key is not found or the event is not in the contract ABI.
    """
    api_key = _get_api_key()
    abi = fetch_contract_abi(contract_address, api_key)
    event_abi = get_event_abi(abi, event_name)
    if event_abi is None:
        raise Exception(f"Event '{event_name}' not found in the ABI.")
    return event_abi


@tool
@handle_exceptions
def get_contract_events(
    contract_address: str,
    event_name: str,
    from_block: Optional[int] = None,
    to_block: Optional[int] = None
) -> List[Any]:
    """
    Fetch events for a given smart contract event within a block range.

    Args:
        contract_address (str): The smart contract address.
        event_name (str): The name of the event to fetch.
        from_block (Optional[int]): The starting block (default: current block - 10).
        to_block (Optional[int]): The ending block (default: current block).

    Returns:
        List[Any]: A list of event logs.

    Raises:
        Exception: If the event is not found in the contract's ABI.
    """
    api_key = _get_api_key()
    abi = fetch_contract_abi(contract_address, api_key)

    web3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    contract = web3.eth.contract(address=contract_address, abi=abi)

    # Resolve the actual event name case-insensitively
    available_events = [e.name for e in contract.events]
    real_event_name = next(
        (e for e in available_events if e.lower() == event_name.lower()), None)

    if not real_event_name:
        raise Exception(
            f"Event '{event_name}' is not in the ABI. Available events: {available_events}"
        )

    event_instance = getattr(contract.events, real_event_name)()

    # Define block range defaults if not provided
    if from_block is None:
        from_block = web3.eth.block_number - 10
    if to_block is None:
        to_block = web3.eth.block_number

    return event_instance.get_logs(from_block=from_block, to_block=to_block)


@tool
@handle_exceptions
def get_latest_eth_block_number() -> int:
    """
    Retrieve the latest Ethereum block number.

    Returns:
        int: The current block number on the Ethereum mainnet.
    """
    web3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    return web3.eth.block_number


@tool
@handle_exceptions
def convert_timestamp_to_block_number(timestamp: int) -> int:
    """
    Convert a Unix timestamp to the nearest Ethereum block number.

    Args:
        timestamp (int): The Unix timestamp.

    Returns:
        int: The block number closest to the provided timestamp.
    """
    api_key = _get_api_key()
    return timestamp_to_block_number(timestamp, api_key)
