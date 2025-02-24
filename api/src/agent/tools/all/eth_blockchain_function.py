import os
import json
import time
import inspect
import requests
import dateparser

from web3 import Web3
from moralis import evm_api
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
def get_current_timestamp() -> int:
    """
    Returns the current timestamp in Unix format.

    Returns:
        str: Current timestamp
    """
    return int(time.time())


@tool
@handle_exceptions
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
                                   inspect.currentframe().f_code.co_name)
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
                                   inspect.currentframe().f_code.co_name)
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
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        raise Exception(
            f"converting block number to timestamp failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}")

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    return timestamp_to_block_number(timestamp, api_key_decrypted)

# GOLDRUSH APIs
# --------------------------
@tool
@handle_exceptions
def get_wallet_activity(wallet_address: str, output_include: list[str]) -> List[dict[str, Any]]:
    """
    Fetch wallet activity for a given address, returning only specified fields.

    Args:
        wallet_address (str):
            The wallet address to retrieve activity for.
        output_include (list[str]):
            A list of field names to include in output.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys 
            listed in `output_include` (if they exist in the source data). 
            Possible fields include:

            - name, chain_id, is_testnet, db_schema_name, label, category_label,
              logo_url, black_logo_url, white_logo_url, color_theme, is_appchain,
              appchain_of.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting wallet activity failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('GOLDRUSH_URL')}/v1/address/{wallet_address}/activity/"
    headers = {'Authorization': f'Bearer {api_key_decrypted}'}
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_balance_for_address(wallet_address: str, output_include: list[str], chain_name: str = "eth-mainnet") -> list[dict]:
    """
    fetch the native, fungible (ERC20), and non-fungible (ERC721 & ERC1155) tokens held by an address

    Args:
        wallet_address (str): The wallet address to retrieve balance for.
        chain_name (str): The chain name to retrieve balance for. Default is eth-mainnet.
        output_include (list[str]):
            A list of field names to include in output.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - contract_decimals, contract_name, contract_ticker_symbol, contract_address, contract_display_name,
              supports_erc, logo_url, logo_urls, last_transferred_at, native_token, type, is_spam, balance, balance_24h,
              quote_rate, quote_rate_24h, quote, quote_24h, pretty_quote, pretty_quote_24h, protocol_metadata.
    """
    currency = "USD"  # TODO: hardcoded for now

    valid_currencies = ["USD", "CAD", "EUR", "SGD", "INR", "JPY", "VND",
                        "CNY", "KRW", "RUB", "TRY", "NGN", "ARS", "AUD", "CHF", "GBP"]
    if currency not in valid_currencies:
        raise ValueError(
            f"Invalid currency. Please choose from: {', '.join(valid_currencies)}")

    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting balance for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('GOLDRUSH_URL')}/v1/{chain_name}/address/{wallet_address}/balances_v2/?quote-currency={currency}"
    headers = {
        'Authorization': f'Bearer {api_key_decrypted}'
    }
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_wallet_transactions(wallet_address: str, output_include: list[str], page: int = 0) -> dict:
    """
    Fetch the transactions involving an address including the decoded log events in a paginated fashion.

    Args:
        wallet_address (str): The wallet address to retrieve transactions for.
        output_include (list[str]): A list of field names to include in output.
        page (int): The page number to retrieve transactions for. starting from 0 and incrementing by 1 until get empty result.

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
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting all transactions for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    chain_name = "eth-mainnet"
    url = f"{os.getenv('GOLDRUSH_URL')}/v1/{chain_name}/address/{wallet_address}/transactions_v3/page/{page}/"
    headers = {
        'Authorization': f'Bearer {api_key_decrypted}',
        "no-logs": "true"
    }
    response = requests.get(url, headers=headers)
    # TODO : limit to 10 for now
    results = json.loads(response.text)["data"]["items"][:10]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_transactions_summary(wallet_address: str, chain_name: str = "eth-mainnet", with_gas: bool = False) -> dict[list]:
    """
    Commonly used to fetch the earliest and latest transactions, and the transaction count for a wallet.
    Calculate the age of the wallet and the time it has been idle and quickly gain insights into their engagement with web3

    Args:
        wallet_address (str): The wallet address to retrieve transactions summary for.
        chain_name (str): The chain name to retrieve transactions summary for. Default is eth-mainnet.
        with_gas (bool): Whether to include gas data in the output.

    Returns:
        List[dict[str, Any]]:
            Output include earliest, latest and count of transactions.

    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting transaction summary for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    url = f"{os.getenv('GOLDRUSH_URL')}/v1/{chain_name}/address/{wallet_address}/transactions_summary/"
    headers = {
        'Authorization': f'Bearer {api_key_decrypted}',
        'with-gas': with_gas
    }
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_transaction_detail(tx_hash: str, output_include: list[str], chain_name: str = "eth-mainnet") -> dict[list]:
    """
    Fetch and render a single transaction including its decoded event logs.

    Args:
        tx_hash (str): The transaction hash to retrieve details for.
        output_include (list[str]): A list of field names to include in output.
        chain_name (str): The chain name to retrieve transaction detail for. Default is eth-mainnet.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - block_signed_at, block_height, block_hash, tx_hash, tx_offset, successful, from_address, miner_address,
                from_address_label, to_address, to_address_label, value, value_quote, pretty_value_quote, gas_metadata,
                gas_offered, gas_spent, gas_price, fees_paid, gas_quote, pretty_gas_quote, gas_quote_rate, explorers,
                log_events, internal_transfers, state_changes, input_data.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting transaction detail for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    chain_name = "eth-mainnet"
    url = f"{os.getenv('GOLDRUSH_URL')}/v1/{chain_name}/transaction_v2/{tx_hash}/"
    headers = {
        'Authorization': f'Bearer {api_key_decrypted}',
        'no-logs': "true"
    }
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


@tool
@handle_exceptions
def get_token_approvals(wallet_address: str, chain_name: str = 'eth-mainnet') -> dict:
    """
    Fetch a list of approvals across all token contracts categorized by spenders for a wallet’s assets.

    Args:
        wallet_address (str): The wallet address to retrieve token approvals for.
        chain_name (str): The chain name to retrieve token approvals for. Default is eth-mainnet.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - token_address, token_address_label, ticker_symbol, contract_decimals, logo_url, quote_rate, balance, balance_quote,
                pretty_balance_quote, value_at_risk, value_at_risk_quote, pretty_value_at_risk_quote, spenders.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting token approvals for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    chain_name = "eth-mainnet"
    url = f"{os.getenv('GOLDRUSH_URL')}/v1/{chain_name}/approvals/{wallet_address}/"
    headers = {
        'Authorization': f'Bearer {api_key_decrypted}'
    }
    response = requests.get(url, headers=headers)
    results = json.loads(response.text)["data"]["items"]

    final_result = []
    for result in results:
        final_result.append({key: result[key]
                             for key in result if key in output_include})

    return final_result


# MORALIS APIs
# --------------------------
@tool
@handle_exceptions
def get_contract_transactions(contract_address: str):
    """
    Fetch latest transactions for a specified contract address.

    Args:
        contract_address (str): Contract address to fetch transactions for.

    Returns:
        dict: list of transactions for the contract.
    """
    db_session = next(get_db())
    api_key = db_session.execute(
        select(Tool.api_key).where(Tool.function_name ==
                                   inspect.currentframe().f_code.co_name)
    ).scalar_one_or_none()

    if api_key is None:
        return f"getting token approvals for wallet failed. {FunctionsErrorCodeEnum.API_KEY_NOT_EXIST.value}"

    api_key_decrypted = decrypt_message(
        message=api_key,
        password=os.getenv("SECRET_KEY"))

    params = {
        "address": contract_address,
        "chain": "eth",
    }

    results = evm_api.transaction.get_wallet_transactions(
        api_key=api_key_decrypted,
        params=params,
    )

    w3 = Web3(Web3.HTTPProvider(os.getenv("ETH_RPC")))
    contract = w3.eth.contract(address=contract_address, abi=get_contract_abi(
        contract_address))

    final_result = []
    for result in results['result']:
        function_name, function_params = contract.decode_function_input(
            result['input'])

        final_result.append({'transaction_hash': result['hash'],
                            'block_number': result['block_number'],
                             'from': result['from_address'],
                             'to': result['to_address'],
                             'value': result['value'],
                             'function_name': function_name,
                             })

    return final_result[:20]
