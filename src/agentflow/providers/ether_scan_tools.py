import os
import json
import time
import requests
import dateparser

from web3 import Web3

from typing import List, Any, Optional, Dict

from src.util.configuration import Config
from src.agentflow.utils.shared_tools import handle_exceptions

from src.agentflow.utils.shared_tools import tool
from hexbytes import HexBytes


class HexJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HexBytes):
            return obj.hex()
        return super().default(obj)


_config = Config.get_config()
_ether_scan_config = Config.get_service_config(_config, "ETHER_SCAN")

_ETHERSCAN_URL = "https://api.etherscan.io/v2/api"
_ETH_RPC = os.environ["ETH_RPC"]


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
    url = _ETHERSCAN_URL
    params = {
        "chainid": "1",
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
def fetch_contract_source_code(contract_address: str, api_key: str) -> str:
    """
    Retrieve the source code of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        api_key (str): The decrypted Etherscan API key.

    Returns:
        str: The contract source code.
    """
    url = _ETHERSCAN_URL
    params = {
        "chainid": "1",
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
def timestamp_to_block_number(timestamp: int, api_key: str) -> int:
    """
    Convert a given Unix timestamp to the nearest Ethereum block number.

    Args:
        timestamp (int): Unix timestamp.
        api_key (str): The decrypted Etherscan API key.

    Returns:
        int: The closest block number.
    """
    url = _ETHERSCAN_URL
    params = {
        "chainid": "1",
        "module": "block",
        "action": "getblocknobytime",
        "timestamp": timestamp,
        "closest": "before",
        "apikey": api_key
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
        output_include (list[str]): A list of field names to include in the output.

    Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - SourceCode, ABI, ContractName, CompilerVersion, OptimizationUsed, Runs,       ConstructorArguments, EVMVersion, Library, LicenseType, Proxy, Implementation, SwarmSource, SimilarMatch

    Notes: if the contract is proxy the `Proxy` field is 1 and there is implementation address
           in `Implementation` field.
    """
    api_key = _ether_scan_config["api_key"]

    response = fetch_contract_source_code(contract_address, api_key)

    final_output = {"proxy": [], "implementation": []}

    current_address = contract_address
    while int(response.get('Proxy', 0)):
        final_output["proxy"].append(response["SourceCode"])
        current_address = response["Implementation"]
        response = fetch_contract_source_code(current_address, api_key)

    final_output["implementation"].append(response["SourceCode"])

    return final_output


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
    api_key = _ether_scan_config["api_key"]
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
    api_key = _ether_scan_config["api_key"]
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
) -> List[Dict[str, Any]]:
    """
    Fetch events for a given smart contract event within a block range.

    Args:
        contract_address (str): The smart contract address.
        event_name (str): The name of the event to fetch.
        from_block (Optional[int]): The starting block (default: current block - 10).
        to_block (Optional[int]): The ending block (default: current block).

    Returns:
        List[Dict[str, Any]]: A list of event logs in JSON serializable format.

    Raises:
        Exception: If the event is not found in the contract's ABI.
    """
    api_key = _ether_scan_config["api_key"]
    abi = fetch_contract_abi(contract_address, api_key)

    web3 = Web3(Web3.HTTPProvider(_ETH_RPC))
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

    logs = event_instance.get_logs(from_block=from_block, to_block=to_block)

    # Convert AttributeDict objects to serializable dictionaries
    serializable_logs = []
    for log in logs:
        log_dict = dict(log)
        # Convert any non-serializable types like HexBytes
        for key, value in log_dict.items():
            if isinstance(value, HexBytes):
                log_dict[key] = value.hex()
            elif isinstance(value, bytes):
                log_dict[key] = value.hex()
        serializable_logs.append(log_dict)

    return serializable_logs


@tool
@handle_exceptions
def get_latest_eth_block_number() -> int:
    """
    Retrieve the latest Ethereum block number.

    Returns:
        int: The current block number on the Ethereum mainnet.
    """
    web3 = Web3(Web3.HTTPProvider(_ETH_RPC))
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
    api_key = _ether_scan_config["api_key"]
    return timestamp_to_block_number(timestamp, api_key)


@tool
@handle_exceptions
def get_latest_eth_block_hash() -> str:
    """
    Retrieve the hash of the latest Ethereum block.

    Returns:
        str: The hash of the latest block on the Ethereum mainnet.
    """
    web3 = Web3(Web3.HTTPProvider(_ETH_RPC))
    latest_block = web3.eth.get_block('latest')
    return web3.to_hex(latest_block.hash)


@tool
@handle_exceptions
def get_block_transactions(block_number: int, output_include: List[str]) -> List[Dict[str, Any]]:
    """
    Retrieve all transactions in a specific Ethereum block.

    Args:
        block_number (int): The block number to retrieve transactions from.

     Returns:
        List[dict[str, Any]]:
            A list of dictionaries where each dictionary only contains the keys
            listed in `output_include` (if they exist in the source data).
            Possible fields include:

            - blockHash, blockNumber, from, gas, gasPrice, maxPriorityFeePerGas, maxFeePerGas,
              hash, input, nonce, to, transactionIndex, value, type, accessList, chainId, v, yParity, r, s
    """
    web3 = Web3(Web3.HTTPProvider(_ETH_RPC))

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
    return final_results


@tool
@handle_exceptions
def decode_transaction_input(transaction_input: str, contract_address: str) -> Dict[str, Any]:
    """
    Decode the input data of an Ethereum transaction using the ABI of the contract.

    Args:
        transaction_input (str): The input data of the transaction (hex string starting with '0x')
        contract_address (str): The address of the contract that was called in the transaction

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
        abi = get_contract_abi(contract_address)

        # Initialize Web3
        web3 = Web3(Web3.HTTPProvider(_ETH_RPC))
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
                            implementation_address)
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
