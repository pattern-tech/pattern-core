import os
import json
import time
import requests
import dateparser

from web3 import Web3
from langchain.tools import tool
from typing import List, Any, Optional, Dict

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions


supported_chain_ids = [
    1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614,
    43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773,
    56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003,
    4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101,
    534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009,
    167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50,
    324, 300
]


def _url_ok(
    url: str,
    *,
    only_https: bool = True,
    no_placeholders: bool = True,
    banned_substrings: List[str] | None = None,
) -> bool:
    if only_https and not url.startswith("https://"):
        return False
    if no_placeholders and "${" in url:
        return False
    return True


def _get_chain_config(chain_id: str) -> Dict:
    _config = {}

    if int(chain_id) in supported_chain_ids:
        _config["RPC"] = get_rpc_url.invoke({"chain_id": int(chain_id)})
        _config["URL"] = "https://api.etherscan.io/v2/api"
        _config["API_KEY"] = os.environ["ETHER_SCAN_API_KEY"]
    else:
        raise ValueError(f"Invalid chain ID: {chain_id}")

    return _config


@handle_exceptions
def fetch_contract_abi(contract_address: str, chain_id: str, api_key: str) -> Dict:
    """
    Retrieve the ABI of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
        api_key (str): The decrypted Etherscan API key.

    Returns:
        Dict: A dictionary representing the contract ABI.
    """
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "contract",
        "action": "getabi",
        "address": contract_address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)

    result = response.json().get("result")
    if result is None:
        raise Exception("No ABI found for the contract.")

    return json.loads(result)


@handle_exceptions
def fetch_contract_source_code(contract_address: str, chain_id: str, api_key: str) -> str:
    """
    Retrieve the source code of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300
        api_key (str): The decrypted Etherscan API key.

    Returns:
        str: The contract source code.
    """
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "contract",
        "action": "getsourcecode",
        "address": contract_address,
        "apikey": api_key
    }
    response = requests.get(url, params=params)

    return response.json()["result"][0]


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
def timestamp_to_block_number(timestamp: int, chain_id: str, api_key: str) -> int:
    """
    Convert a given Unix timestamp to the nearest Ethereum block number.

    Args:
        timestamp (int): Unix timestamp.
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
        api_key (str): The decrypted Etherscan API key.

    Returns:
        int: The closest block number.
    """
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    return int(response.json()["result"])


@tool
def get_rpc_url(chain_id: int) -> Optional[str]:
    """
    Retrieves a valid RPC URL for a specified blockchain network.

    Args:
        chain_id (int): The chain ID to find an RPC URL for
    Returns:
        Optional[str]: A valid RPC URL for the specified chain ID, or None if no
                      suitable RPC URL was found
    """
    source_url = "https://chainlist.org/rpcs.json"
    resp = requests.get(source_url, timeout=10)
    resp.raise_for_status()
    all_chains = resp.json()

    for entry in all_chains:
        if entry.get("chainId") != chain_id:
            continue

        for raw in entry.get("rpc", []):
            # ChainList sometimes gives dicts like {"url": "..."} – normalise
            rpc_url = (
                raw
                if isinstance(raw, str)
                else raw.get("url")               # most common field
                or raw.get("address")             # fallback seen in some lists
                if isinstance(raw, dict)
                else None
            )
            if rpc_url and _url_ok(rpc_url):
                return rpc_url
        break  # we found the chain, no acceptable RPCs

    return None


@tool
@handle_exceptions
def get_contract_source_code(contract_address: str, chain_id: str) -> str:
    """
    Retrieve the source code of a smart contract.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        str: The contract source code.
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]

    response = fetch_contract_source_code(contract_address, chain_id, api_key)

    final_output = {"proxy": [], "implementation": []}

    current_address = contract_address
    while int(response.get('Proxy', 0)):
        final_output["proxy"].append(response["SourceCode"])
        current_address = response["Implementation"]
        response = fetch_contract_source_code(
            current_address, chain_id, api_key)

    final_output["implementation"].append(response["SourceCode"])

    return final_output


@tool
@handle_exceptions
def get_contract_abi(contract_address: str, chain_id: str) -> Dict:
    """
    Retrieve the ABI of a smart contract.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        Dict: The contract ABI.
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]

    final_output = {"proxy": [], "implementation": []}

    response = fetch_contract_source_code(contract_address, chain_id, api_key)

    current_address = contract_address
    while int(response.get('Proxy', 0)):
        final_output["proxy"].append(json.loads(response["ABI"]))
        current_address = response["Implementation"]
        response = fetch_contract_source_code(
            current_address, chain_id, api_key)

    final_output["implementation"].append(json.loads(response["ABI"]))

    return final_output


@tool
@handle_exceptions
def get_abi_of_event(contract_address: str, chain_id: str, event_name: str) -> Dict:
    """
    Retrieve the ABI of a specific event from a smart contract.

    Args:
        contract_address (str): The smart contract address.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300
        event_name (str): The name of the event.

    Returns:
        Dict: The ABI of the specified event.

    Raises:
        Exception: If the API key is not found or the event is not in the contract ABI.
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    abi = fetch_contract_abi(contract_address, chain_id, api_key)
    event_abi = get_event_abi(abi, event_name)
    if event_abi is None:
        raise Exception(f"Event '{event_name}' not found in the ABI.")
    return event_abi


@tool
@handle_exceptions
def get_contract_events(
    contract_address: str,
    chain_id: str,
    event_name: str,
    from_block: Optional[int] = None,
    to_block: Optional[int] = None
) -> List[Any]:
    """
    Fetch events for a given smart contract event within a block range.

    Args:
        contract_address (str): The smart contract address.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300
        event_name (str): The name of the event to fetch.
        from_block (Optional[int]): The starting block (default: current block - 10).
        to_block (Optional[int]): The ending block (default: current block).

    Returns:
        List[Any]: A list of event logs.

    Raises:
        Exception: If the event is not found in the contract's ABI.
    """
    contract_address = Web3.to_checksum_address(contract_address)

    api_key = _get_chain_config(chain_id)["API_KEY"]
    abi = fetch_contract_abi(contract_address, chain_id, api_key)

    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
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
def get_latest_chain_block_number(chain_id: str) -> int:
    """
    Retrieve the latest chain block number.

    Args:
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        int: The current block number on the Ethereum mainnet.
    """
    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
    return web3.eth.block_number


@tool
@handle_exceptions
def convert_timestamp_to_block_number(timestamp: int, chain_id: str) -> int:
    """
    Convert a Unix timestamp to the nearest Ethereum block number.

    Args:
        timestamp (int): The Unix timestamp.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        int: The block number closest to the provided timestamp.
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    return timestamp_to_block_number(timestamp, chain_id, api_key)


@tool
@handle_exceptions
def get_latest_eth_block_hash(chain_id: str) -> str:
    """
    Retrieve the hash of the latest chain block.

    Args:
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        str: The hash of the latest block on the Ethereum mainnet.
    """
    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
    latest_block = web3.eth.get_block('latest')
    return web3.to_hex(latest_block.hash)


@tool
@handle_exceptions
def get_block_transactions(block_number: int, chain_id: str, output_include: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve all transactions in a specific Ethereum block.

    Args:
        block_number (int): The block number to retrieve transactions from.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300
        output_include (List[str]): List of fields to include in the output.

     Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - blockHash, blockNumber, from, gas, gasPrice, maxPriorityFeePerGas, maxFeePerGas,
              hash, input, nonce, to, transactionIndex, value, type, accessList, chainId, v, yParity, r, s
    """
    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    # Validate block number
    latest_block = web3.eth.block_number
    if block_number < 0 or block_number >= latest_block:
        raise ValueError(f"Block number must be between 0 and {latest_block}")

    # Get the block with all transactions
    block = web3.eth.get_block(block_number, full_transactions=True)

    # Process transactions to make them JSON serializable
    transactions = []
    for tx in block.transactions:
        # Convert transaction to dictionary
        if isinstance(tx, dict):
            tx_dict = tx
        else:
            tx_dict = dict(tx)

        # Convert non-serializable objects to strings
        for key, value in tx_dict.items():
            if isinstance(value, bytes):
                tx_dict[key] = web3.to_hex(value)
            elif isinstance(value, int) and key == 'value':
                # Convert Wei to Ether for readability
                tx_dict[key] = web3.from_wei(value, 'ether')

        transactions.append(tx_dict)

    final_results = []
    for result in transactions:
        final_results.append({item: result[item]
                              for item in result.keys() if item in output_include})
    return str(final_results)


@tool
@handle_exceptions
def decode_transaction_input(transaction_input: str, contract_address: str, chain_id: str) -> Dict[str, Any]:
    """
    Decode the input data of an Ethereum transaction using the ABI of the contract.

    Args:
        transaction_input (str): The input data of the transaction (hex string starting with '0x')
        contract_address (str): The address of the contract that was called in the transaction
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300

    Returns:
        Dict[str, Any]: A dictionary containing the decoded transaction input with the following fields:
            - function_name: The name of the function that was called
            - function_signature: The signature of the function (e.g., 'transfer(address,uint256)')
            - parameters: A list of dictionaries, each containing:
                - name: The parameter name
                - type: The parameter type
                - value: The parameter value (decoded)

    Raises:
        Exception: If the input data cannot be decoded or the contract ABI cannot be retrieved
    """
    # Validate input
    if not transaction_input.startswith('0x'):
        raise ValueError("Transaction input must start with '0x'")

    if len(transaction_input) < 10:  # '0x' + 8 chars (4 bytes)
        return {
            "error": "Transaction input too short to contain a function selector",
            "raw_input": transaction_input
        }

    # Get the function selector (first 4 bytes/8 hex chars after '0x')
    function_selector = transaction_input[:10]  # includes '0x'

    try:
        # Get the contract ABI
        abi = get_contract_abi(contract_address, chain_id)

        # Initialize Web3
        web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
        contract = web3.eth.contract(address=contract_address, abi=abi)

        # Try direct decoding first using web3.py's built-in functionality
        try:
            function_obj, decoded_params = contract.decode_function_input(
                transaction_input)

            # If we get here, decoding succeeded
            function_name = function_obj.fn_name
            function_inputs = [param for param in function_obj.abi['inputs']]

            # Create the function signature string
            input_types = [input.get('type') for input in function_inputs]
            function_signature_str = f"{function_name}({','.join(input_types)})"

            # Format the parameters for output
            parameters = []
            for param in function_inputs:
                param_name = param.get('name')
                param_type = param.get('type')
                param_value = decoded_params.get(param_name)

                # Convert bytes and addresses to readable format
                if isinstance(param_value, bytes):
                    param_value = web3.to_hex(param_value)
                elif param_type.startswith('address') and isinstance(param_value, str):
                    param_value = param_value.lower()  # Normalize address
                elif param_type.startswith('uint') or param_type.startswith('int'):
                    # Keep as int but convert large numbers to string to avoid JSON serialization issues
                    if isinstance(param_value, int) and (param_value > 9007199254740991 or param_value < -9007199254740991):
                        param_value = str(param_value)

                parameters.append({
                    "name": param_name,
                    "type": param_type,
                    "value": param_value
                })

            return {
                "function_name": function_name,
                "function_signature": function_signature_str,
                "parameters": parameters
            }

        except Exception as decode_error:
            # If direct decoding fails, fall back to manual method
            # Find the matching function in the ABI
            function = None
            all_selectors = []

            for item in abi:
                if item.get('type') == 'function':
                    # Calculate the function selector
                    fn_name = item.get('name', '')
                    input_types = [input.get('type')
                                   for input in item.get('inputs', [])]
                    fn_signature = f"{fn_name}({','.join(input_types)})"

                    # Calculate selector correctly - only first 4 bytes (8 hex chars) after '0x'
                    calculated_selector = '0x' + \
                        web3.keccak(text=fn_signature).hex()[2:10]
                    all_selectors.append((calculated_selector, fn_signature))

                    if calculated_selector == function_selector:
                        function = item
                        break

            if not function:
                # Try to get implementation contract if this might be a proxy
                try:
                    # Check for common proxy patterns
                    # EIP-1967 proxy implementation slot
                    implementation_slot = '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc'
                    implementation_address = web3.eth.get_storage_at(
                        Web3.to_checksum_address(contract_address),
                        implementation_slot
                    )

                    # Convert to address format (last 20 bytes)
                    if implementation_address and int(implementation_address.hex(), 16) != 0:
                        implementation_address = '0x' + \
                            implementation_address.hex()[-40:]

                        # Try with implementation ABI
                        implementation_abi = get_contract_abi(
                            implementation_address, chain_id)
                        implementation_contract = web3.eth.contract(
                            address=contract_address,
                            abi=implementation_abi
                        )

                        # Try decoding with implementation contract
                        function_obj, decoded_params = implementation_contract.decode_function_input(
                            transaction_input)

                        # If we get here, decoding succeeded with implementation contract
                        return {
                            "function_name": function_obj.fn_name,
                            "function_signature": f"{function_obj.fn_name}({','.join([i['type'] for i in function_obj.abi['inputs']])})",
                            "parameters": [
                                {
                                    "name": param.get('name'),
                                    "type": param.get('type'),
                                    "value": decoded_params.get(param.get('name'))
                                }
                                for param in function_obj.abi['inputs']
                            ],
                            "note": "Decoded using implementation contract ABI"
                        }
                except Exception as proxy_error:
                    # Proxy detection failed, continue with original error
                    pass

                # If we get here, both direct decoding and proxy detection failed
                return {
                    "error": "Function signature not found in contract ABI",
                    "function_selector": function_selector,
                    # Show first 10 known selectors for debugging
                    "known_selectors": all_selectors[:10],
                    "raw_input": transaction_input,
                    "decode_error": str(decode_error)
                }

            # If we found the function through manual matching, try to decode
            try:
                # Decode the function inputs
                function_name = function.get('name')
                function_inputs = function.get('inputs', [])

                # Create the function signature string
                input_types = [input.get('type') for input in function_inputs]
                function_signature_str = f"{function_name}({','.join(input_types)})"

                # Try to decode parameters using the contract object
                decoded_params = contract.decode_function_input(
                    transaction_input)

                # Format the parameters for output
                parameters = []
                for param in function_inputs:
                    param_name = param.get('name')
                    param_type = param.get('type')
                    param_value = decoded_params[1].get(param_name)

                    # Convert bytes and addresses to readable format
                    if isinstance(param_value, bytes):
                        param_value = web3.to_hex(param_value)
                    elif param_type.startswith('address') and isinstance(param_value, str):
                        param_value = param_value.lower()  # Normalize address
                    elif param_type.startswith('uint') or param_type.startswith('int'):
                        # Keep as int but convert large numbers to string to avoid JSON serialization issues
                        if isinstance(param_value, int) and (param_value > 9007199254740991 or param_value < -9007199254740991):
                            param_value = str(param_value)

                    parameters.append({
                        "name": param_name,
                        "type": param_type,
                        "value": param_value
                    })

                return {
                    "function_name": function_name,
                    "function_signature": function_signature_str,
                    "parameters": parameters
                }
            except Exception as manual_decode_error:
                return {
                    "error": f"Found function signature but failed to decode parameters: {str(manual_decode_error)}",
                    "function_name": function.get('name'),
                    "function_signature": function_signature_str,
                    "raw_input": transaction_input
                }

    except Exception as e:
        return {
            "error": f"Failed to decode transaction input: {str(e)}",
            "raw_input": transaction_input,
            "function_selector": function_selector
        }


@tool
@handle_exceptions
def call_contract_function(contract_address: str, chain_id: str, function_name: str, function_params: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Call a read-only (view/pure) function of a smart contract and return its result to get data from contract

    Args:
        contract_address (str): The address of the smart contract.
        chain_id (str): The chain ID can be 1, 11155111, 17000, 2741, 11124, 33111, 33139, 42170, 42161, 421614, 43114, 43113, 8453, 84532, 80094, 80069, 199, 1028, 81457, 168587773, 56, 97, 44787, 42220, 25, 252, 2522, 100, 59144, 59141, 5000, 5003, 4352, 43521, 1287, 1284, 1285, 10, 11155420, 80002, 137, 2442, 1101, 534352, 534351, 57054, 146, 50104, 531050104, 1923, 1924, 167009, 167000, 130, 1301, 1111, 1112, 480, 4801, 660279, 37714555429, 51, 50, 324, 300
        function_name (str): The name of the function to call.
        function_params (Optional[List[Any]]): List of parameters to pass to the function. Default is None (no parameters).

    Returns:
        Dict[str, Any]: A dictionary containing the following fields:
            - success: Boolean indicating if the call was successful
            - result: The result of the function call if successful
            - error: Error message if unsuccessful
            - result_type: The data type of the result

    Raises:
        Exception: If the contract ABI cannot be retrieved or the function call fails
    """
    # Initialize parameters if None
    if function_params is None:
        function_params = []

    api_key = _get_chain_config(chain_id)["API_KEY"]
    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    try:
        # Get the contract ABI
        contract_address = Web3.to_checksum_address(contract_address)
        implementation_contract_address = contract_address
        # Check if the contract address is a proxy and get the implementation address
        if int(fetch_contract_source_code(contract_address, chain_id, api_key).get('Proxy', 0)):
            implementation_contract_address = fetch_contract_source_code(
                contract_address, chain_id, api_key)["Implementation"]
            implementation_contract_address = Web3.to_checksum_address(
                implementation_contract_address)

        abi = fetch_contract_abi(
            implementation_contract_address, chain_id, api_key)

        contract = web3.eth.contract(address=contract_address, abi=abi)

        # Find the function in the ABI
        function_entries = [f for f in abi if f.get(
            'type') == 'function' and f.get('name') == function_name]
        if not function_entries:
            available_functions = [f['name']
                                   for f in abi if f.get('type') == 'function']
            raise Exception(
                f"Function '{function_name}' not found in contract ABI. Available functions: {available_functions}")

        # Get the function object
        function_obj = getattr(contract.functions, function_name)

        # Check if the function is read-only
        function_entry = function_entries[0]
        if function_entry.get('stateMutability') not in ['view', 'pure', 'constant']:
            raise Exception(
                f"Function '{function_name}' is not a read-only function and might modify state or require a transaction.")

        # Get function outputs for later use
        function_outputs = function_entry.get('outputs', [])

        # Call the function with provided parameters
        result = function_obj(*function_params).call()

        # Process the result
        result_type = "unknown"
        processed_result = result

        # Determine result type and format accordingly
        if isinstance(result, (int, float, bool, str)):
            result_type = type(result).__name__
        elif isinstance(result, bytes):
            processed_result = web3.to_hex(result)
            result_type = "bytes (hex)"
        # Handle both tuple and list results - Web3.py may return either depending on the version
        elif isinstance(result, (tuple, list)):
            # If we have output definitions, create a dictionary with proper names
            if function_outputs and len(function_outputs) == len(result):
                processed_result = {}
                for i, output in enumerate(function_outputs):
                    output_name = output.get('name')
                    if not output_name:  # If name is empty, use index
                        output_name = f"output_{i}"

                    value = result[i]
                    processed_result[output_name] = value

                    # Handle special types
                    if isinstance(value, bytes):
                        processed_result[output_name] = web3.to_hex(value)
                    # For large integers, preserve the original value
                    # but also provide the ether conversion for convenience
                    elif isinstance(value, int) and value > 10**10:
                        processed_result[f"{output_name}_eth"] = web3.from_wei(
                            value, 'ether')

                result_type = "struct"
            else:
                # Fallback to list if we can't match outputs
                processed_result = list(result)
                processed_result = [web3.to_hex(v) if isinstance(
                    v, bytes) else v for v in processed_result]
                result_type = "tuple"

        response = {
            "success": True,
            "result": processed_result,
            "result_type": function_outputs,
        }

        return response

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None,
            "result_type": None
        }


# New Etherscan API method implementations

# === ACCOUNTS METHODS ===

@tool
@handle_exceptions
def get_account_balance(address: str, chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the Ether balance of a given address.

    Args:
        address (str): The Ethereum address to check
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: A dictionary containing the balance in wei and ether
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        balance_wei = int(result["result"])
        web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
        balance_eth = web3.from_wei(balance_wei, 'ether')
        return {
            "success": True,
            "balance_wei": balance_wei,
            "balance_eth": float(balance_eth),
            "address": address
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def get_multi_account_balance(addresses: List[str], chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the Ether balance of multiple addresses in a single call.

    Args:
        addresses (List[str]): List of Ethereum addresses to check
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: A dictionary containing the balance for each address
    """
    if len(addresses) > 20:
        raise ValueError("Maximum 20 addresses allowed in a single call")

    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "balancemulti",
        "address": ",".join(addresses),
        "tag": "latest",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        results = []
        web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

        for account in result["result"]:
            balance_wei = int(account["balance"])
            balance_eth = web3.from_wei(balance_wei, 'ether')
            results.append({
                "address": account["account"],
                "balance_wei": balance_wei,
                "balance_eth": float(balance_eth)
            })

        return {
            "success": True,
            "accounts": results
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def get_normal_transactions(address: str, chain_id: str, start_block: int = 0,
                            end_block: int = 99999999, page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves normal transactions for an address.

    Args:
        address (str): The address to get transactions for
        chain_id (str): The chain ID
        start_block (int, optional): Starting block number. Defaults to 0.
        end_block (int, optional): Ending block number. Defaults to 99999999.
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of normal transactions
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": offset,
        "sort": "desc",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    result = response.json()

    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    if result["status"] == "1":
        transactions = result["result"]
        for tx in transactions:
            if "value" in tx:
                # Convert Wei to Ether for readability
                tx["value_eth"] = float(
                    web3.from_wei(int(tx["value"]), 'ether'))

        return {
            "success": True,
            "transactions": transactions,
            "count": len(transactions)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No transactions found"),
            "result": []
        }


@tool
@handle_exceptions
def get_internal_transactions(address: str, chain_id: str, start_block: int = 0,
                              end_block: int = 99999999, page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves internal transactions for an address.

    Args:
        address (str): The address to get transactions for
        chain_id (str): The chain ID
        start_block (int, optional): Starting block number. Defaults to 0.
        end_block (int, optional): Ending block number. Defaults to 99999999.
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of internal transactions
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "txlistinternal",
        "address": address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": offset,
        "sort": "desc",
        "apikey": api_key
    }
    response = requests.get(url, params=params)
    result = response.json()

    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    if result["status"] == "1":
        transactions = result["result"]
        for tx in transactions:
            if "value" in tx:
                # Convert Wei to Ether for readability
                tx["value_eth"] = float(
                    web3.from_wei(int(tx["value"]), 'ether'))

        return {
            "success": True,
            "internal_transactions": transactions,
            "count": len(transactions)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No internal transactions found"),
            "result": []
        }


@tool
@handle_exceptions
def get_erc20_token_transfers(address: str, chain_id: str, contract_address: str = None,
                              start_block: int = 0, end_block: int = 99999999,
                              page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves ERC20 token transfer events for an address.

    Args:
        address (str): The address to get token transfers for
        chain_id (str): The chain ID
        contract_address (str, optional): The token contract address. Defaults to None.
        start_block (int, optional): Starting block number. Defaults to 0.
        end_block (int, optional): Ending block number. Defaults to 99999999.
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of token transfers
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": offset,
        "sort": "desc",
        "apikey": api_key
    }

    if contract_address:
        params["contractaddress"] = contract_address

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        transfers = result["result"]
        for transfer in transfers:
            if "value" in transfer and "decimals" in transfer:
                # Convert token value based on decimals
                decimals = int(transfer["decimals"])
                value = int(transfer["value"]) / (10 ** decimals)
                transfer["token_value"] = value

        return {
            "success": True,
            "erc20_transfers": transfers,
            "count": len(transfers)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No token transfers found"),
            "result": []
        }


@tool
@handle_exceptions
def get_erc721_token_transfers(address: str, chain_id: str, contract_address: str = None,
                               start_block: int = 0, end_block: int = 99999999,
                               page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves ERC721 (NFT) token transfer events for an address.

    Args:
        address (str): The address to get NFT transfers for
        chain_id (str): The chain ID
        contract_address (str, optional): The NFT contract address. Defaults to None.
        start_block (int, optional): Starting block number. Defaults to 0.
        end_block (int, optional): Ending block number. Defaults to 99999999.
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of NFT transfers
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "tokennfttx",
        "address": address,
        "startblock": start_block,
        "endblock": end_block,
        "page": page,
        "offset": offset,
        "sort": "desc",
        "apikey": api_key
    }

    if contract_address:
        params["contractaddress"] = contract_address

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        transfers = result["result"]
        return {
            "success": True,
            "erc721_transfers": transfers,
            "count": len(transfers)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No NFT transfers found"),
            "result": []
        }


@tool
@handle_exceptions
def get_blocks_mined_by_address(address: str, chain_id: str, page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves the blocks mined by an address.

    Args:
        address (str): The miner address
        chain_id (str): The chain ID
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of blocks mined by the address
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "getminedblocks",
        "address": address,
        "blocktype": "blocks",
        "page": page,
        "offset": offset,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        blocks = result["result"]
        return {
            "success": True,
            "mined_blocks": blocks,
            "count": len(blocks)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No mined blocks found"),
            "result": []
        }


# === TRANSACTIONS METHODS ===

@tool
@handle_exceptions
def get_transaction_status(txhash: str, chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the status of a transaction.

    Args:
        txhash (str): Transaction hash
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Transaction status information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "transaction",
        "action": "getstatus",
        "txhash": txhash,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        status_info = result["result"]
        return {
            "success": True,
            "transaction_status": status_info
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Transaction status not found"),
            "result": None
        }


@tool
@handle_exceptions
def get_transaction_receipt_status(txhash: str, chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the receipt status of a transaction.

    Args:
        txhash (str): Transaction hash
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Transaction receipt status (0=Failed, 1=Success)
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "transaction",
        "action": "gettxreceiptstatus",
        "txhash": txhash,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        receipt_status = result["result"]
        status = int(receipt_status.get("status", "0"))
        return {
            "success": True,
            "receipt_status": status,
            "status_message": "Success" if status == 1 else "Failed"
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Transaction receipt status not found"),
            "result": None
        }


# === BLOCKS METHODS ===

@tool
@handle_exceptions
def get_block_reward(block_number: int, chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the block reward and fee information.

    Args:
        block_number (int): Block number
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Block reward and fee information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "block",
        "action": "getblockreward",
        "blockno": block_number,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))

    if result["status"] == "1":
        reward_info = result["result"]
        # Convert values from wei to ether for readability
        if "blockReward" in reward_info:
            reward_info["blockReward_eth"] = float(
                web3.from_wei(int(reward_info["blockReward"]), 'ether'))

        return {
            "success": True,
            "block_reward": reward_info
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Block reward information not found"),
            "result": None
        }


@tool
@handle_exceptions
def get_block_countdown(block_number: int, chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the estimated time remaining until a specific block is mined.

    Args:
        block_number (int): Target future block number
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Block countdown information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "block",
        "action": "getblockcountdown",
        "blockno": block_number,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        countdown_info = result["result"]
        return {
            "success": True,
            "countdown": countdown_info
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Block countdown information not found"),
            "result": None
        }


@tool
@handle_exceptions
def get_estimated_block_time(chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the current estimate for block time (in seconds).

    Args:
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Estimated block time in seconds
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "block",
        "action": "getblocktime",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        block_time = int(result["result"])
        return {
            "success": True,
            "estimated_block_time_seconds": block_time
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Block time information not found"),
            "result": None
        }


# === LOGS METHODS ===

@tool
@handle_exceptions
def get_logs(address: str, from_block: int, to_block: int, chain_id: str,
             topic0: str = None, topic1: str = None, topic2: str = None,
             topic3: str = None, topic0_1_opr: str = None,
             topic1_2_opr: str = None, topic2_3_opr: str = None) -> Dict[str, Any]:
    """
    Retrieves logs for specified address and topics.

    Args:
        address (str): Address to get logs for
        from_block (int): Start block number
        to_block (int): End block number
        chain_id (str): The chain ID
        topic0 (str, optional): Topic 0. Defaults to None.
        topic1 (str, optional): Topic 1. Defaults to None.
        topic2 (str, optional): Topic 2. Defaults to None.
        topic3 (str, optional): Topic 3. Defaults to None.
        topic0_1_opr (str, optional): Operator between topic0 and topic1 (and/or). Defaults to None.
        topic1_2_opr (str, optional): Operator between topic1 and topic2 (and/or). Defaults to None.
        topic2_3_opr (str, optional): Operator between topic2 and topic3 (and/or). Defaults to None.

    Returns:
        Dict[str, Any]: Log events
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "logs",
        "action": "getLogs",
        "address": address,
        "fromBlock": from_block,
        "toBlock": to_block,
        "apikey": api_key
    }

    # Add optional parameters if provided
    if topic0:
        params["topic0"] = topic0
    if topic1:
        params["topic1"] = topic1
    if topic2:
        params["topic2"] = topic2
    if topic3:
        params["topic3"] = topic3
    if topic0_1_opr:
        params["topic0_1_opr"] = topic0_1_opr
    if topic1_2_opr:
        params["topic1_2_opr"] = topic1_2_opr
    if topic2_3_opr:
        params["topic2_3_opr"] = topic2_3_opr

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        logs = result["result"]
        return {
            "success": True,
            "logs": logs,
            "count": len(logs)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No logs found"),
            "result": []
        }


# === GETH/PARITY PROXY METHODS ===

@tool
@handle_exceptions
def eth_block_number(chain_id: str) -> Dict[str, Any]:
    """
    Returns the number of most recent block using the eth_blockNumber method.

    Args:
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Current block number in hex and decimal
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "proxy",
        "action": "eth_blockNumber",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "result" in result:
        hex_number = result["result"]
        decimal_number = int(hex_number, 16)
        return {
            "success": True,
            "hex_block_number": hex_number,
            "block_number": decimal_number
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def eth_get_block_by_number(block_number: str, include_txs: bool, chain_id: str) -> Dict[str, Any]:
    """
    Returns information about a block by block number using eth_getBlockByNumber.

    Args:
        block_number (str): Block number in hex (e.g. '0x1b4') or tag (e.g. 'latest')
        include_txs (bool): True for full transaction objects, False for transaction hashes
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Block information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "proxy",
        "action": "eth_getBlockByNumber",
        "tag": block_number,
        "boolean": "true" if include_txs else "false",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "result" in result:
        return {
            "success": True,
            "block": result["result"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def eth_get_transaction_by_hash(txhash: str, chain_id: str) -> Dict[str, Any]:
    """
    Returns information about a transaction by hash using eth_getTransactionByHash.

    Args:
        txhash (str): Transaction hash
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Transaction information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "proxy",
        "action": "eth_getTransactionByHash",
        "txhash": txhash,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "result" in result:
        tx = result["result"]

        # Convert numeric values to decimal for better readability
        if tx:
            web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
            if "value" in tx:
                tx["value_decimal"] = int(tx["value"], 16)
                tx["value_eth"] = float(
                    web3.from_wei(tx["value_decimal"], 'ether'))

            if "gas" in tx:
                tx["gas_decimal"] = int(tx["gas"], 16)

            if "gasPrice" in tx:
                tx["gasPrice_decimal"] = int(tx["gasPrice"], 16)
                tx["gasPrice_gwei"] = float(
                    web3.from_wei(tx["gasPrice_decimal"], 'gwei'))

        return {
            "success": True,
            "transaction": tx
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def eth_get_transaction_receipt(txhash: str, chain_id: str) -> Dict[str, Any]:
    """
    Returns receipt of a transaction by hash using eth_getTransactionReceipt.

    Args:
        txhash (str): Transaction hash
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Transaction receipt information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "proxy",
        "action": "eth_getTransactionReceipt",
        "txhash": txhash,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "result" in result:
        receipt = result["result"]

        # Add human-readable status if available
        if receipt and "status" in receipt:
            status_code = int(receipt["status"], 16)
            receipt["status_description"] = "Success" if status_code == 1 else "Failed"

        return {
            "success": True,
            "receipt": receipt
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "result": None
        }


@tool
@handle_exceptions
def eth_call(to: str, data: str, chain_id: str, block: str = "latest") -> Dict[str, Any]:
    """
    Executes a new message call without creating a transaction on the blockchain.

    Args:
        to (str): Address to execute call on
        data (str): The compiled code of a function call, e.g. web3.sha3("balanceOf(address)").slice(0, 10) + "000000000000000000000000" + address removing "0x" from the address
        chain_id (str): The chain ID
        block (str, optional): Block number in hex or tag. Defaults to "latest".

    Returns:
        Dict[str, Any]: Result of the call
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "proxy",
        "action": "eth_call",
        "to": to,
        "data": data,
        "tag": block,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if "result" in result:
        return {
            "success": True,
            "call_result": result["result"]
        }
    else:
        return {
            "success": False,
            "error": result.get("error", {}).get("message", "Unknown error"),
            "result": None
        }


# === TOKENS METHODS ===

@tool
@handle_exceptions
def get_token_supply(contract_address: str, chain_id: str) -> Dict[str, Any]:
    """
    Returns the total supply of a specific ERC-20 token contract.

    Args:
        contract_address (str): The token contract address
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Token supply information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "tokensupply",
        "contractaddress": contract_address,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        # Get token decimals to format the result properly
        try:
            web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
            contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address),
                                         abi=[{
                                             "constant": True,
                                             "inputs": [],
                                             "name": "decimals",
                                             "outputs": [{"name": "", "type": "uint8"}],
                                             "payable": False,
                                             "stateMutability": "view",
                                             "type": "function"
                                         }])
            decimals = contract.functions.decimals().call()
            raw_supply = int(result["result"])
            formatted_supply = raw_supply / (10 ** decimals)

            return {
                "success": True,
                "raw_supply": raw_supply,
                "decimals": decimals,
                "formatted_supply": formatted_supply
            }
        except Exception as e:
            # If we can't get decimals, return raw supply
            return {
                "success": True,
                "raw_supply": int(result["result"]),
                "error_getting_decimals": str(e)
            }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get token supply"),
            "result": None
        }


@tool
@handle_exceptions
def get_token_account_balance(contract_address: str, address: str, chain_id: str) -> Dict[str, Any]:
    """
    Returns the token balance of a specific account for a specific token contract.

    Args:
        contract_address (str): The token contract address
        address (str): The account address to check
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Token balance information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": contract_address,
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        # Get token decimals to format the result properly
        try:
            web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
            contract = web3.eth.contract(address=Web3.to_checksum_address(contract_address),
                                         abi=[{
                                             "constant": True,
                                             "inputs": [],
                                             "name": "decimals",
                                             "outputs": [{"name": "", "type": "uint8"}],
                                             "payable": False,
                                             "stateMutability": "view",
                                             "type": "function"
                                         }])
            decimals = contract.functions.decimals().call()
            raw_balance = int(result["result"])
            formatted_balance = raw_balance / (10 ** decimals)

            return {
                "success": True,
                "raw_balance": raw_balance,
                "decimals": decimals,
                "formatted_balance": formatted_balance,
                "address": address
            }
        except Exception as e:
            # If we can't get decimals, return raw balance
            return {
                "success": True,
                "raw_balance": int(result["result"]),
                "address": address,
                "error_getting_decimals": str(e)
            }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get token balance"),
            "result": None
        }


# === GAS TRACKER METHODS ===

@tool
@handle_exceptions
def get_gas_oracle(chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the current Safe, Proposed and Fast gas prices.

    Args:
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: Gas price estimates
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "gastracker",
        "action": "gasoracle",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        gas_oracle = result["result"]
        return {
            "success": True,
            "gas_oracle": gas_oracle
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get gas oracle"),
            "result": None
        }


# === STATS METHODS ===

@tool
@handle_exceptions
def get_eth_price(chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the latest price of ETH in USD and BTC.

    Args:
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: ETH price information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "ethprice",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        price_info = result["result"]
        return {
            "success": True,
            "eth_price_usd": float(price_info.get("ethusd", 0)),
            "eth_price_btc": float(price_info.get("ethbtc", 0)),
            "timestamp": price_info.get("ethusd_timestamp")
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get ETH price"),
            "result": None
        }


@tool
@handle_exceptions
def get_eth_supply(chain_id: str) -> Dict[str, Any]:
    """
    Retrieves the total supply of ETH.

    Args:
        chain_id (str): The chain ID

    Returns:
        Dict[str, Any]: ETH supply information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "ethsupply",
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        supply_wei = int(result["result"])
        web3 = Web3(Web3.HTTPProvider(_get_chain_config(chain_id)["RPC"]))
        supply_eth = float(web3.from_wei(supply_wei, 'ether'))

        return {
            "success": True,
            "supply_wei": supply_wei,
            "supply_eth": supply_eth
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get ETH supply"),
            "result": None
        }


@tool
@handle_exceptions
def get_eth_daily_market_cap(chain_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves the daily market capitalization of ETH.

    Args:
        chain_id (str): The chain ID
        start_date (str): Start date in yyyy-MM-dd format
        end_date (str): End date in yyyy-MM-dd format

    Returns:
        Dict[str, Any]: ETH daily market cap information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "ethdailymarketcap",
        "startdate": start_date,
        "enddate": end_date,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        market_cap_data = result["result"]
        return {
            "success": True,
            "market_cap_data": market_cap_data
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get daily market cap"),
            "result": None
        }


@tool
@handle_exceptions
def get_eth_daily_price(chain_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves the historical daily price of ETH.

    Args:
        chain_id (str): The chain ID
        start_date (str): Start date in yyyy-MM-dd format
        end_date (str): End date in yyyy-MM-dd format

    Returns:
        Dict[str, Any]: ETH daily price information
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "ethdailyprice",
        "startdate": start_date,
        "enddate": end_date,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        price_data = result["result"]
        return {
            "success": True,
            "price_data": price_data
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get daily price"),
            "result": None
        }


# === L2 DEPOSITS/WITHDRAWALS METHODS ===

@tool
@handle_exceptions
def get_l2_deposits(address: str, l2chain: str, chain_id: str, page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves Layer 2 deposits for a given address.

    Args:
        address (str): The address to get deposits for
        l2chain (str): Layer 2 chain (e.g., "optimism", "arbitrum", "base")
        chain_id (str): The chain ID
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of layer 2 deposits
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "l2deposits",
        "address": address,
        "l2chain": l2chain,
        "page": page,
        "offset": offset,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        deposits = result["result"]
        return {
            "success": True,
            "deposits": deposits,
            "count": len(deposits)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No deposits found"),
            "result": []
        }


@tool
@handle_exceptions
def get_l2_withdrawals(address: str, l2chain: str, chain_id: str, page: int = 1, offset: int = 10) -> Dict[str, Any]:
    """
    Retrieves Layer 2 withdrawals for a given address.

    Args:
        address (str): The address to get withdrawals for
        l2chain (str): Layer 2 chain (e.g., "optimism", "arbitrum", "base")
        chain_id (str): The chain ID
        page (int, optional): Page number. Defaults to 1.
        offset (int, optional): Max records to return. Defaults to 10.

    Returns:
        Dict[str, Any]: List of layer 2 withdrawals
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "l2withdrawals",
        "address": address,
        "l2chain": l2chain,
        "page": page,
        "offset": offset,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        withdrawals = result["result"]
        return {
            "success": True,
            "withdrawals": withdrawals,
            "count": len(withdrawals)
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "No withdrawals found"),
            "result": []
        }


# === USAGE METHODS ===

@tool
@handle_exceptions
def get_daily_network_usage(chain_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves daily network statistics.

    Args:
        chain_id (str): The chain ID
        start_date (str): Start date in yyyy-MM-dd format
        end_date (str): End date in yyyy-MM-dd format

    Returns:
        Dict[str, Any]: Daily network usage statistics
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "dailynetworkstats",
        "startdate": start_date,
        "enddate": end_date,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        network_stats = result["result"]
        return {
            "success": True,
            "network_stats": network_stats
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get daily network stats"),
            "result": None
        }


@tool
@handle_exceptions
def get_daily_network_utilization(chain_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves daily network utilization statistics.

    Args:
        chain_id (str): The chain ID
        start_date (str): Start date in yyyy-MM-dd format
        end_date (str): End date in yyyy-MM-dd format

    Returns:
        Dict[str, Any]: Daily network utilization statistics
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "dailynetworkutilization",
        "startdate": start_date,
        "enddate": end_date,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        network_utilization = result["result"]
        return {
            "success": True,
            "network_utilization": network_utilization
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get daily network utilization"),
            "result": None
        }


@tool
@handle_exceptions
def get_daily_average_gas_price(chain_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Retrieves daily average gas price.

    Args:
        chain_id (str): The chain ID
        start_date (str): Start date in yyyy-MM-dd format
        end_date (str): End date in yyyy-MM-dd format

    Returns:
        Dict[str, Any]: Daily average gas price statistics
    """
    api_key = _get_chain_config(chain_id)["API_KEY"]
    url = _get_chain_config(chain_id)["URL"]
    params = {
        "chainid": chain_id,
        "module": "stats",
        "action": "dailyavggasprice",
        "startdate": start_date,
        "enddate": end_date,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] == "1":
        gas_price_data = result["result"]
        return {
            "success": True,
            "gas_price_data": gas_price_data
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "Failed to get daily average gas price"),
            "result": None
        }
