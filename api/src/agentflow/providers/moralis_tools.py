import os

from web3 import Web3
from moralis import evm_api
from langchain.tools import tool
from typing import List, Dict, Any

from src.agentflow.utils.shared_tools import handle_exceptions


def _get_api_key() -> str:
    """
    Retrieve the Moralis API key from the environment.

    Returns:
        str: The Moralis API key.

    Raises:
        Exception: If the API key is not found.
    """
    api_key = os.getenv("MORALIS_API_KEY")
    if not api_key:
        raise Exception("No API key found for Moralis.")
    return api_key


@tool
@handle_exceptions
def get_contract_transactions(contract_address: str) -> List[Dict[str, Any]]:
    """
    Fetch the latest transactions for a specified contract address using the Moralis API 
    and decode their function inputs.

    Args:
        contract_address (str): The contract address to fetch transactions for.

    Returns:
        List[Dict[str, Any]]: A list of decoded transaction details, limited to 20 entries.
    """
    # Retrieve API key
    api_key = _get_api_key()

    # Set up parameters for the Moralis API call
    params = {
        "address": contract_address,
        "chain": "eth"
    }

    # Call the Moralis API to get wallet transactions
    results = evm_api.transaction.get_wallet_transactions(
        api_key=api_key,
        params=params,
    )

    # Set up a Web3 provider
    eth_rpc = os.getenv("ETH_RPC")
    if not eth_rpc:
        raise Exception("ETH_RPC environment variable is not set.")
    w3 = Web3(Web3.HTTPProvider(eth_rpc))

    # Retrieve the contract ABI.
    # NOTE: Adjust the import path for get_contract_abi as needed.
    from src.agent.tools.some_module import get_contract_abi
    contract_abi = get_contract_abi(contract_address)

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    decoded_transactions: List[Dict[str, Any]] = []
    for tx in results.get('result', []):
        try:
            # Attempt to decode the function input.
            # If the input is empty or invalid, an exception may be raised.
            decoded_input = contract.decode_function_input(
                tx.get('input', '0x'))
            function_name = decoded_input[0].fn_name if decoded_input else None
        except Exception:
            function_name = None

        decoded_transactions.append({
            'transaction_hash': tx.get('hash'),
            'block_number': tx.get('block_number'),
            'from': tx.get('from_address'),
            'to': tx.get('to_address'),
            'value': tx.get('value'),
            'function_name': function_name,
        })

    return decoded_transactions[:20]
