import os
import json
import time
import inspect
import requests
import dateparser

from web3 import Web3
from typing import List, Any
from sqlalchemy import select
from langchain.tools import tool

from src.db.models import Tool
from src.db.sql_alchemy import Database
from src.util.encryption import decrypt_message
from src.shared.error_code import FunctionsErrorCodeEnum
from src.agent.tools.shared_tools import handle_exceptions, timeout


database = Database()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@handle_exceptions
@timeout(seconds=10)
def fetch_contract_abi(address: str, api_key: str) -> dict:
    """
    Retrieves the ABI of a smart contract from Etherscan API.

    Args:
        address (str): The contract address to get ABI for
        api_key (str): Etherscan API key

    Returns:
        dict: JSON response containing the contract ABI
    """
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": "1",
        "module": "contract",
        "action": "getabi",
        "address": address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)

    return json.loads(response.json()["result"])


@handle_exceptions
@timeout(seconds=10)
def fetch_contract_source_code(address: str, api_key: str) -> dict:
    """
    Retrieves the source code of a smart contract from Etherscan API.

    Args:
        address (str): The contract address to get source code for
        api_key (str, optional): Etherscan API key. Defaults to a provided key.

    Returns:
        dict: JSON response containing the contract source code and metadata
    """
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": "1",
        "module": "contract",
        "action": "getsourcecode",
        "address": address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    return response.json()["result"][0]["SourceCode"]


@handle_exceptions
@timeout(seconds=10)
def get_event_abi(abi: list, event_name: str) -> dict:
    """
    Get the ABI entry for a specific event name.

    Args:
        abi (list): List of ABI entries containing event definitions
        event_name (str): Name of the event to find

    Returns:
        dict: ABI entry for the specified event, or None if not found
    """
    for item in abi:
        if item.get("type") == "event" and item.get("name") == event_name:
            return item
    return None


@handle_exceptions
@timeout(seconds=10)
def timestamp_to_block_number(timestamp: int, api_key: str) -> int:
    """Convert Ethereum timestamp to nearest block number.

    Args:
        timestamp (int): Unix timestamp to query
        api_key (str): Etherscan API key

    Returns:
        int: Block number closest to the given timestamp

    Raises:
        requests.exceptions.RequestException: If API request fails
        KeyError: If response is missing expected fields
    """
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": "1",
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    return response.json()["result"]


@tool
@handle_exceptions
@timeout(seconds=10)
def get_current_timestamp() -> int:
    """
    Returns the current timestamp in Unix format.

    Returns:
        str: Current timestamp
    """
    return int(time.time())


@tool
@handle_exceptions
@timeout(seconds=10)
def convert_to_timestamp(date_str: str) -> int:
    """
    Convert a date string to Unix timestamp.

    Args:
        date_str (str): Date string in natural language format (e.g. "one month ago", "12/3/2020")

    Returns:
        int: Unix timestamp representing the parsed date

    Raises:
        ValueError: If the date string cannot be parsed
        Exception: For other parsing errors
    """
    parsed_date = dateparser.parse(date_str)

    if parsed_date:
        return int(time.mktime(parsed_date.timetuple()))
    else:
        raise ValueError(f"Could not parse the date string: {date_str}")


@tool
@handle_exceptions
@timeout(seconds=10)
def get_contract_source_code(contract_address: str) -> str:
    """
    Retrieves the source code of a smart contract from Etherscan API.

    Args:
        contract_address (str): The contract address to get source code for

    Returns:
        str: The source code of the contract
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting contract source code failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    contract_source_code = fetch_contract_source_code(
        contract_address, api_key_decrypted)
    return contract_source_code


@tool
@handle_exceptions
@timeout(seconds=10)
def get_contract_abi(contract_address: str) -> dict:
    """
    Retrieves the ABI of a smart contract from Etherscan API.

    Args:
        address (str): The contract address to get ABI for

    Returns:
        dict: JSON response containing the contract ABI
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting contract source code failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    contract_abi = fetch_contract_abi(
        contract_address, api_key_decrypted)
    return contract_abi


@tool
@handle_exceptions
@timeout(seconds=10)
def get_abi_of_event(contract_address: str, event_name: str) -> dict:
    """
    Retrieves the ABI of a specific event from a smart contract.

    Args:
        contract_address (str): The address of the smart contract
        event_name (str): The name of the event to retrieve the ABI for

    Returns:
        dict: ABI of the specified event, or None if not found

    Raises:
        Exception: If the API key is not found or decryption fails
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   "fetch_contract_abi")
    ).scalar_one_or_none()

    if api_key is None:
        raise Exception(
            f"getting contract abi failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}")

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    abi = fetch_contract_abi(contract_address, api_key_decrypted)
    return get_event_abi(abi, event_name)


@tool
@handle_exceptions
@timeout(seconds=10)
def get_contract_events(
        contract_address: str,
        event_name: str,
        from_block: int = None,
        to_block: int = None) -> List[Any]:
    """
    Fetches events from a smart contract within a specified block range.

    Args:
        contract_address (str): The address of the smart contract
        event_name (str): Name of the event to fetch
        from_block (int): Starting block number to fetch events from (default: current block - 10)
        to_block (int): Ending block number to fetch events to (default: current block)

    Returns:
        List[Any]: List of events found within the block range

    Raises:
        Exception: For any other unexpected errors
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   "fetch_contract_abi")
    ).scalar_one_or_none()

    if api_key is None:
        raise Exception(
            f"getting contract abi failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}")

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    abi = fetch_contract_abi(
        contract_address, api_key_decrypted)

    web3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    contract = web3.eth.contract(address=contract_address, abi=abi)

    available_events = [c.name for c in contract.events]
    real_event_name = ""
    for e in available_events:
        if event_name.lower() == e.lower():
            real_event_name = e

    if real_event_name == "":
        raise Exception(
            f"event {event_name} is not in the ABI event list. The available events are {available_events}")

    events = getattr(contract.events, real_event_name)()

    if events is None:
        return []

    if from_block is None:
        from_block = (web3.eth.block_number-10)

    if to_block is None:
        to_block = web3.eth.block_number

    logs = events.get_logs(
        from_block=from_block,
        to_block=to_block
    )

    return logs


@tool
@handle_exceptions
@timeout(seconds=10)
def get_latest_eth_block_number() -> int:
    """
    Gets the latest Ethereum block number from the blockchain.

    Returns:
        int: The current block number on the Ethereum mainnet

    Raises:
        Web3ConnectionError: If unable to connect to Ethereum node
    """
    web3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    return web3.eth.block_number


@tool
@handle_exceptions
@timeout(seconds=10)
def get_contract_transactions(contract_address: str, from_block: int, to_block: int) -> list:
    """
    Get all transactions for a given contract address between specified block range.

    Args:
        contract_address (str): Ethereum contract address to query
        from_block (int): Starting block number
        to_block (int): Ending block number

    Returns:
        list: List of dictionaries containing transaction details with fields:
            - from: Address that sent the transaction
            - to: Address that received the transaction
            - function_name: Name of the contract function called
            - function_params: Parameters passed to the function
    """
    w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    contract = w3.eth.contract(
        address=contract_address, abi=get_contract_abi(contract_address))

    result = []
    for x in range(from_block, to_block):
        block = w3.eth.get_block(x, True)
        for transaction in block.transactions:
            if transaction['to'] == contract_address or transaction['from'] == contract_address:
                function, function_params = contract.decode_function_input(
                    f"0x{transaction.input.hex()}")
                result.append({
                    "from": transaction['from'],
                    "to": transaction['to'],
                    "function_name": function.name,
                    "function_params": function_params,
                    "block_number": transaction['blockNumber']
                })
    return result


@tool
@handle_exceptions
@timeout(seconds=10)
def convert_timestamp_to_block_number(timestamp: int) -> int:
    """Convert Ethereum timestamp to nearest block number.

    Args:
        timestamp (int): Unix timestamp to query

    Returns:
        int: Block number closest to the given timestamp
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   "fetch_contract_abi")
    ).scalar_one_or_none()

    if api_key is None:
        raise Exception(
            f"converting block number to timestamp failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}")

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    return timestamp_to_block_number(timestamp, api_key_decrypted)
