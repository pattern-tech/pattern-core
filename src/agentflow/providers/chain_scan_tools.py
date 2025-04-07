# Standard library imports
import os
import json
import time

# Third-party imports
import requests
import dateparser
from web3 import Web3
from typing import List, Optional, Dict

# Internal imports
from src.agentflow.models.chain_scan import *
from src.agentflow.utils.shared_tools import tool, handle_exceptions
from src.agentflow.models.chain_scan.chain_scan_models import (
    EventParameter,
    ContractEvent,
    BlockTransaction,
    DecodedParameter)


def _get_chain_config(chain_id: str) -> Dict:
    _config = {}
    if chain_id == "1":
        _config["RPC"] = os.environ["ETH_RPC"]
        _config["URL"] = "https://api.etherscan.io/v2/api"
        _config["API_KEY"] = os.environ["ETHER_SCAN_API_KEY"]
    elif chain_id == "42161":
        _config["RPC"] = os.environ["ARBITRUM_ONE_RPC"]
        _config["URL"] = "https://api.arbiscan.io/api"
        _config["API_KEY"] = os.environ["ARBI_SCAN_API_KEY"]
    elif chain_id == "8453":
        _config["RPC"] = os.environ["BASE_RPC"]
        _config["URL"] = "https://api.basescan.org/api"
        _config["API_KEY"] = os.environ["BASE_SCAN_API_KEY"]
    elif chain_id == "137":
        _config["RPC"] = os.environ["POLYGON_RPC"]
        _config["URL"] = "https://api.polygonscan.com/api"
        _config["API_KEY"] = os.environ["POLYGON_SCAN_API_KEY"]
    elif chain_id == "250":
        _config["RPC"] = os.environ["FANTOM_RPC"]
        _config["URL"] = "https://api.ftmscan.com/api"
        _config["API_KEY"] = os.environ["FTM_SCAN_API_KEY"]
    else:
        raise ValueError(f"Invalid chain ID: {chain_id}")

    return _config


@handle_exceptions
def fetch_contract_abi(contract_address: str, chain_id: str, api_key: str) -> Dict:
    """
    Retrieve the ABI of a smart contract from the Etherscan API.

    Args:
        contract_address (str): The contract address.
        chain_id (str): The chain ID can be 1, 42161, 8453
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
        chain_id (str): The chain ID can be 1, 42161, 8453, 137, 250
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
@handle_exceptions
def get_current_timestamp() -> CurrentTimestampResponse:
    """
    Get the current Unix timestamp.

    Returns:
        CurrentTimestampResponse: The current Unix timestamp.
    """
    return int(time.time())


@tool
@handle_exceptions
def convert_to_timestamp(input_data: ConvertToTimestampInput) -> TimestampResponse:
    """
    Convert a natural language date string into a Unix timestamp.

    Args:
        input_data: Input parameters including the date string. Can be either a ConvertToTimestampInput model or a dictionary.

    Returns:
        TimestampResponse: The Unix timestamp corresponding to the provided date.

    Raises:
        ValueError: If the date string cannot be parsed.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = ConvertToTimestampInput(**input_data)
    else:
        input_model = input_data

    parsed_date = dateparser.parse(input_model.date_str)
    if parsed_date:
        return int(time.mktime(parsed_date.timetuple()))
    else:
        raise ValueError(
            f"Could not parse the date string: {input_model.date_str}")


@tool
@handle_exceptions
def get_contract_source_code(input_data: ContractSourceCodeInput) -> ContractSourceCodeResponse:
    """
    Retrieve the source code of a smart contract.

    Args:
        input_data: Input parameters including contract address and chain ID. Can be either a ContractSourceCodeInput model or a dictionary.

    Returns:
        ContractSourceCodeResponse: The contract source code and related information.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = ContractSourceCodeInput(**input_data)
    else:
        input_model = input_data

    try:
        api_key = _get_chain_config(input_model.chain_id)["API_KEY"]
        response = fetch_contract_source_code(
            input_model.contract_address, input_model.chain_id, api_key)
    except Exception as e:
        if "Invalid chain ID" in str(e):
            raise ValueError(
                f"Invalid chain ID: {input_model.chain_id}. Supported chain IDs are: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")
        else:
            raise

    return response


@tool
@handle_exceptions
def get_contract_abi(input_data: ContractAbiInput) -> ContractAbiResponse:
    """
    Retrieve the ABI of a smart contract.

    Args:
        input_data: Input parameters including contract address and chain ID. Can be either a ContractAbiInput model or a dictionary.

    Returns:
        ContractAbiResponse: The contract ABI.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = ContractAbiInput(**input_data)
    else:
        input_model = input_data

    api_key = _get_chain_config(input_model.chain_id)["API_KEY"]
    abi = fetch_contract_abi(
        input_model.contract_address, input_model.chain_id, api_key)
    return abi


@tool
@handle_exceptions
def get_abi_of_event(input_data: EventAbiOfContractInput) -> EventAbiResponse:
    """
    Retrieve the ABI of a specific event from a smart contract.

    Args:
        input_data: Input parameters including contract address, chain ID, and event name. Can be either an EventAbiOfContractInput model or a dictionary.

    Returns:
        EventAbiResponse: The ABI of the specified event.

    Raises:
        Exception: If the API key is not found or the event is not in the contract ABI.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = EventAbiOfContractInput(**input_data)
    else:
        input_model = input_data

    api_key = _get_chain_config(input_model.chain_id)["API_KEY"]
    abi = fetch_contract_abi(input_model.contract_address,
                             input_model.chain_id, api_key)
    event_abi = get_event_abi(abi, input_model.event_name)

    if event_abi is None:
        available_events = [item["name"]
                            for item in abi if item.get("type") == "event"]
        raise Exception(
            f"Event '{input_model.event_name}' not found in contract ABI. Available events: {available_events}")

    # Create and return an EventAbiResponse instance
    return event_abi


@tool
@handle_exceptions
def get_contract_events(input_data: ContractEventsInput) -> ContractEventsResponse:
    """
    Fetch events for a given smart contract event within a block range.

    Args:
        input_data: Input parameters including contract address, chain ID, event name, and optional block range.

    Returns:
        ContractEventsResponse: A list of events emitted by the contract.

    Raises:
        Exception: If the event is not found in the contract's ABI.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = ContractEventsInput(**input_data)
    else:
        input_model = input_data

    api_key = _get_chain_config(input_model.chain_id)["API_KEY"]

    web3 = Web3(Web3.HTTPProvider(
        _get_chain_config(input_model.chain_id)["RPC"]))

    # Get the contract ABI
    abi = fetch_contract_abi(input_model.contract_address,
                             input_model.chain_id, api_key)
    contract = web3.eth.contract(address=Web3.to_checksum_address(
        input_model.contract_address), abi=abi)

    # Get the event ABI
    event_abi = get_event_abi(abi, input_model.event_name)
    if event_abi is None:
        available_events = [item["name"]
                            for item in abi if item.get("type") == "event"]
        raise Exception(
            f"Event '{input_model.event_name}' not found in contract ABI. Available events: {available_events}")

    # Determine block range
    to_block = input_model.to_block
    if to_block is None:
        to_block = web3.eth.block_number

    # Create event filter
    event_filter = contract.events[input_model.event_name].create_filter(
        fromBlock=input_model.from_block,
        toBlock=to_block
    )

    # Get all entries
    entries = event_filter.get_all_entries()

    # Process events
    contract_events = []
    for event in entries:
        # Create parameters list from event arguments
        parameters = []
        for arg_name, arg_value in event.args.items():
            # Find parameter type from event ABI
            param_type = None
            for input_param in event_abi.get('inputs', []):
                if input_param.get('name') == arg_name:
                    param_type = input_param.get('type')
                    break

            # Convert bytes to hex if needed
            if isinstance(arg_value, bytes):
                arg_value = web3.to_hex(arg_value)

            # Create EventParameter instance
            parameters.append(EventParameter(
                name=arg_name,
                type=param_type,
                value=arg_value
            ))

        # Create ContractEvent instance
        contract_events.append(ContractEvent(
            event_name=input_model.event_name,
            block_number=event.blockNumber,
            transaction_hash=event.transactionHash.hex(),
            address=input_model.contract_address,
            parameters=parameters
        ))

    # Return ContractEventsResponse instance
    return ContractEventsResponse(events=contract_events)


@tool
@handle_exceptions
def get_latest_chain_block_number(input_data: LatestBlockNumberInput) -> BlockNumberResponse:
    """
    Retrieve the latest chain block number.

    Args:
        input_data: Input parameters including chain ID.

    Returns:
        BlockNumberResponse: The current block number on the specified blockchain.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = LatestBlockNumberInput(**input_data)
    else:
        input_model = input_data

    web3 = Web3(Web3.HTTPProvider(
        _get_chain_config(input_model.chain_id)["RPC"]))
    return web3.eth.block_number


@tool
@handle_exceptions
def convert_timestamp_to_block_number(input_data: TimestampToBlockNumberInput) -> BlockNumberResponse:
    """
    Convert a Unix timestamp to the nearest blockchain block number.

    Args:
        input_data: Input parameters including timestamp and chain ID.

    Returns:
        BlockNumberResponse: The block number closest to the provided timestamp.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = TimestampToBlockNumberInput(**input_data)
    else:
        input_model = input_data

    api_key = _get_chain_config(input_model.chain_id)["API_KEY"]
    block_number = timestamp_to_block_number(
        input_model.timestamp, input_model.chain_id, api_key)
    return block_number


@tool
@handle_exceptions
def get_latest_eth_block_hash(input_data: LatestBlockHashInput) -> BlockHashResponse:
    """
    Retrieve the hash of the latest chain block.

    Args:
        input_data: Input parameters including chain ID.

    Returns:
        BlockHashResponse: The hash of the latest block on the specified blockchain.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = LatestBlockHashInput(**input_data)
    else:
        input_model = input_data

    web3 = Web3(Web3.HTTPProvider(
        _get_chain_config(input_model.chain_id)["RPC"]))
    block = web3.eth.get_block('latest')
    return block.hash.hex()


@tool
@handle_exceptions
def get_block_transactions(input_data: BlockTransactionsInput) -> BlockTransactionsResponse:
    """
    Retrieve all transactions in a specific blockchain block.

    Args:
        input_data: Input parameters including block number, chain ID, and output fields.

    Returns:
        BlockTransactionsResponse: A list of transactions in the specified block.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = BlockTransactionsInput(**input_data)
    else:
        input_model = input_data

    web3 = Web3(Web3.HTTPProvider(
        _get_chain_config(input_model.chain_id)["RPC"]))

    # Get the block with transactions
    block = web3.eth.get_block(
        input_model.block_number, full_transactions=True)
    transactions = block.transactions

    # Process transactions to include only requested fields
    block_transactions = []
    for tx in transactions:
        # Convert AttributeDict to regular dict
        tx_dict = dict(tx)

        # Convert bytes to hex strings for better readability
        for k, v in tx_dict.items():
            if isinstance(v, bytes):
                tx_dict[k] = web3.to_hex(v)
            elif isinstance(v, int) and k == 'value':
                # Convert Wei to Ether for readability
                tx_dict[k] = web3.from_wei(v, 'ether')

        # Filter fields based on output_include
        if input_model.output_include and len(input_model.output_include) > 0:
            filtered_tx = {k: v for k, v in tx_dict.items(
            ) if k in input_model.output_include}
        else:
            filtered_tx = tx_dict

    return filtered_tx


@tool
@handle_exceptions
def decode_transaction_input(input_data: DecodeTransactionInput) -> DecodeTransactionResponse:
    """
    Decode the input data of an Ethereum transaction using the ABI of the contract.

    Args:
        input_data: Input parameters including transaction input data, contract address, and chain ID.

    Returns:
        DecodeTransactionResponse: A dictionary containing the decoded transaction input with function name, signature, and parameters.

    Raises:
        Exception: If the contract ABI cannot be retrieved or the transaction input cannot be decoded.
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = DecodeTransactionInput(**input_data)
    else:
        input_model = input_data

    # Validate input
    if not input_model.transaction_input.startswith('0x'):
        raise ValueError("Transaction input must start with '0x'")

    if len(input_model.transaction_input) < 10:  # '0x' + 8 chars (4 bytes)
        return {
            "error": "Transaction input too short to contain a function selector",
            "raw_input": input_model.transaction_input
        }

    # Get the function selector (first 4 bytes/8 hex chars after '0x')
    function_selector = input_model.transaction_input[:10]  # includes '0x'

    try:
        # Get the contract ABI
        abi = get_contract_abi({
            "contract_address": input_model.contract_address,
            "chain_id": input_model.chain_id
        })

        # Initialize Web3
        web3 = Web3(Web3.HTTPProvider(
            _get_chain_config(input_model.chain_id)["RPC"]))
        contract = web3.eth.contract(
            address=input_model.contract_address, abi=abi)

        # Try direct decoding first using web3.py's built-in functionality
        try:
            function_obj, decoded_params = contract.decode_function_input(
                input_model.transaction_input)

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

            # Create DecodedParameter instances
            decoded_parameters = []
            for param in parameters:
                decoded_parameters.append(DecodedParameter(
                    name=param["name"],
                    type=param["type"],
                    value=param["value"]
                ))

            # Return DecodeTransactionResponse instance
            return DecodeTransactionResponse(
                function_name=function_name,
                function_signature=function_signature_str,
                parameters=decoded_parameters
            )

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
                        Web3.to_checksum_address(input_model.contract_address),
                        implementation_slot
                    )

                    # Convert to address format (last 20 bytes)
                    if implementation_address and int(implementation_address.hex(), 16) != 0:
                        implementation_address = '0x' + \
                            implementation_address.hex()[-40:]

                        # Try with implementation ABI
                        implementation_abi = get_contract_abi({
                            "contract_address": implementation_address,
                            "chain_id": input_model.chain_id
                        })
                        implementation_contract = web3.eth.contract(
                            address=input_model.contract_address,
                            abi=implementation_abi
                        )

                        # Try decoding with implementation contract
                        function_obj, decoded_params = implementation_contract.decode_function_input(
                            input_model.transaction_input)

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
                    "raw_input": input_model.transaction_input,
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
                    input_model.transaction_input)

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

                # Create DecodedParameter instances
                decoded_parameters = []
                for param in parameters:
                    decoded_parameters.append(DecodedParameter(
                        name=param["name"],
                        type=param["type"],
                        value=param["value"]
                    ))

                # Return DecodeTransactionResponse instance
                return DecodeTransactionResponse(
                    function_name=function_name,
                    function_signature=function_signature_str,
                    parameters=decoded_parameters
                )
            except Exception as manual_decode_error:
                # Return a DecodeTransactionResponse with minimal information
                return DecodeTransactionResponse(
                    function_name=function.get('name'),
                    function_signature=function_signature_str,
                    parameters=[]
                )

    except Exception as e:
        # Return a minimal DecodeTransactionResponse for error cases
        return DecodeTransactionResponse(
            function_name="unknown",
            function_signature="unknown",
            parameters=[]
        )


@tool
@handle_exceptions
def call_contract_function(input_data: ContractFunctionCallInput) -> ContractFunctionCallResponse:
    """
    Call a read-only function on a smart contract and return the result.

    Args:
        input_data: Input parameters including contract address, chain ID, function name, and optional function parameters.

    Returns:
        ContractFunctionCallResponse: A dictionary containing:
            - success: Boolean indicating if the call was successful
            - result: The result of the function call
            - error: Error message if unsuccessful
            - result_type: The data type of the result

    Raises:
        Exception: If the contract ABI cannot be retrieved or the function call fails
    """
    # Convert dictionary to Pydantic model if needed
    if isinstance(input_data, dict):
        input_model = ContractFunctionCallInput(**input_data)
    else:
        input_model = input_data

    # Initialize parameters if None
    function_params = input_model.function_params or []

    api_key = _get_chain_config(input_model.chain_id)["API_KEY"]
    web3 = Web3(Web3.HTTPProvider(
        _get_chain_config(input_model.chain_id)["RPC"]))

    try:
        # Get the contract ABI
        contract_address = Web3.to_checksum_address(
            input_model.contract_address)
        abi = fetch_contract_abi(
            contract_address, input_model.chain_id, api_key)
        contract = web3.eth.contract(address=contract_address, abi=abi)

        # Find the function in the ABI
        function_entries = [f for f in abi if f.get(
            'type') == 'function' and f.get('name') == input_model.function_name]
        if not function_entries:
            available_functions = [f['name']
                                   for f in abi if f.get('type') == 'function']
            raise Exception(
                f"Function '{input_model.function_name}' not found in contract ABI. Available functions: {available_functions}")

        # Get the function object
        function_obj = getattr(contract.functions, input_model.function_name)

        # Check if the function is read-only
        function_entry = function_entries[0]
        if function_entry.get('stateMutability') not in ['view', 'pure', 'constant']:
            raise Exception(
                f"Function '{input_model.function_name}' is not a read-only function and might modify state or require a transaction.")

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
        elif isinstance(result, tuple):
            # Handle named tuples (common in Solidity returns)
            if hasattr(result, '_asdict'):
                processed_result = dict(result._asdict())
                result_type = "struct"
            else:
                processed_result = list(result)
                result_type = "tuple"

            # Convert any bytes in the result to hex
            if isinstance(processed_result, dict):
                for key, value in processed_result.items():
                    if isinstance(value, bytes):
                        processed_result[key] = web3.to_hex(value)
                    # Large ints might be wei values
                    elif isinstance(value, int) and value > 10**10:
                        processed_result[f"{key}_eth"] = web3.from_wei(
                            value, 'ether')
            elif isinstance(processed_result, list):
                processed_result = [web3.to_hex(v) if isinstance(
                    v, bytes) else v for v in processed_result]
        elif isinstance(result, list):
            processed_result = result
            result_type = "array"
            # Convert any bytes in the list to hex
            for i, item in enumerate(processed_result):
                if isinstance(item, bytes):
                    processed_result[i] = web3.to_hex(item)

        return {
            "success": True,
            "result": processed_result,
            "result_type": result_type
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": None,
            "result_type": None
        }
