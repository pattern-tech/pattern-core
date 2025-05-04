import json
import requests
import functools
from unittest import mock

from src.agentflow.providers.chain_scan_tools import *
from src.agentflow.utils.shared_tools import log_method

# Test constants
chain_id = "50"  # Ethereum mainnet
ethereum_contract_address = "0xd9374f1438967bddd41f4186facf2c34d7226004"  # DAI token
ethereum_tx_input = "0xa9059cbb0000000000000000000000008894e0a0c962cb723c1976a4421c95949be2d4e300000000000000000000000000000000000000000000000001158e460913d00000"  # Example transfer tx
ethereum_block_number = 18000000  # Example block number
ethereum_event_name = "Transfer"  # Common event name


@log_method
def test_get_contract_source_code():
    source_code = get_contract_source_code.invoke({
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id
    })

    assert source_code is not None
    assert "proxy" in source_code
    assert "implementation" in source_code

    return source_code


@log_method
def test_get_contract_abi():
    abi = get_contract_abi.invoke({
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id
    })
    assert abi is not None
    assert "proxy" in abi
    assert "implementation" in abi

    return abi


@log_method
def test_get_abi_of_event():
    event_abi = get_abi_of_event.invoke({
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id,
        "event_name": ethereum_event_name
    })
    assert event_abi is not None
    assert event_abi["type"] == "event"
    assert event_abi["name"] == ethereum_event_name

    return event_abi


@log_method
def test_get_contract_events():
    # Get the latest block number for testing
    latest_block = get_latest_chain_block_number.invoke({
        "chain_id": chain_id
    })

    # Get events from a small range of blocks
    events = get_contract_events.invoke({
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id,
        "event_name": ethereum_event_name,
        "from_block": latest_block - 10,
        "to_block": latest_block
    })

    # The test might pass even if no events are found in this range
    assert events is not None

    return events


@log_method
def test_get_latest_chain_block_number():
    block_number = get_latest_chain_block_number.invoke({
        "chain_id": chain_id
    })
    assert block_number is not None
    assert isinstance(block_number, int)
    assert block_number > 0

    return block_number


@log_method
def test_convert_timestamp_to_block_number():
    # Current timestamp (seconds since epoch)
    timestamp = int(time.time())

    block_number = convert_timestamp_to_block_number.invoke({
        "timestamp": timestamp,
        "chain_id": chain_id
    })
    assert block_number is not None
    assert isinstance(block_number, int)
    assert block_number > 0

    return block_number


@log_method
def test_get_latest_eth_block_hash():
    block_hash = get_latest_eth_block_hash.invoke({
        "chain_id": chain_id
    })
    assert block_hash is not None
    assert block_hash.startswith("0x")
    assert len(block_hash) == 66  # '0x' + 64 hex chars

    return block_hash


@log_method
def test_get_block_transactions():
    transactions = get_block_transactions.invoke({
        "block_number": ethereum_block_number,
        "chain_id": chain_id,
        "output_include": ["hash", "from", "to", "value"]
    })
    assert transactions is not None

    return transactions


@log_method
def test_decode_transaction_input():
    decoded_input = decode_transaction_input.invoke({
        "transaction_input": ethereum_tx_input,
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id
    })
    assert decoded_input is not None
    # It should either have function_name or error
    assert "function_name" in decoded_input or "error" in decoded_input

    return decoded_input


@log_method
def test_call_contract_function():
    # Call a common view function like name() or symbol()
    result = call_contract_function.invoke({
        "contract_address": ethereum_contract_address,
        "chain_id": chain_id,
        "function_name": "symbol"
    })
    assert result is not None
    assert "success" in result

    # If success is True, check for result
    if result["success"]:
        assert "result" in result
    else:
        assert "error" in result

    return result


if __name__ == "__main__":
    test_get_contract_source_code()
    test_get_contract_abi()
    test_get_abi_of_event()
    test_get_latest_chain_block_number()
    # Run this test after getting latest block number
    test_get_contract_events()
    test_convert_timestamp_to_block_number()
    test_get_latest_eth_block_hash()
    test_get_block_transactions()
    test_decode_transaction_input()
    test_call_contract_function()
