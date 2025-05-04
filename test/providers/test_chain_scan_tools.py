import json
import requests
import functools
from unittest import mock
import datetime

from src.agentflow.providers.chain_scan_tools import *
from src.agentflow.utils.shared_tools import log_method

# Test constants
chain_id = "1"  # Ethereum mainnet
ethereum_contract_address = "0x52B04F8e6aeEAe5d8c9c135f79fbA166826026B1"  # DAI token
ethereum_tx_input = "0xa9059cbb0000000000000000000000008894e0a0c962cb723c1976a4421c95949be2d4e300000000000000000000000000000000000000000000000001158e460913d00000"  # Example transfer tx
ethereum_block_number = 18000000  # Example block number
ethereum_event_name = "Transfer"  # Common event name

# Example address (vitalik.eth)
ethereum_address = "0x810CbaC7bc8C13ba83C8e8a64C00D6F8Fc98bE1A"
# Example transaction hash
ethereum_transaction_hash = "0x396288e0ad6690159d56b5502a172d54baea649698b4d7af2393cf5d98bf1bb3"
erc20_token_address = "0xb47e3cd837ddf8e4c57f05d70ab865de6e193bbb"
erc721_token_address = "0x000000000000003607fce1ac9e043a86675c5c2f" 


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

# === ACCOUNTS METHODS TESTS ===


@log_method
def test_get_account_balance():
    balance = get_account_balance.invoke({
        "address": ethereum_address,
        "chain_id": chain_id
    })
    assert balance is not None
    assert "success" in balance
    if balance["success"]:
        assert "balance_wei" in balance
        assert "balance_eth" in balance
        assert isinstance(balance["balance_wei"], int)
        assert isinstance(balance["balance_eth"], float)

    return balance


@log_method
def test_get_multi_account_balance():
    balances = get_multi_account_balance.invoke({
        "addresses": [ethereum_address, ethereum_contract_address],
        "chain_id": chain_id
    })
    assert balances is not None
    assert "success" in balances
    if balances["success"]:
        assert "accounts" in balances
        assert len(balances["accounts"]) > 0
        assert "address" in balances["accounts"][0]
        assert "balance_wei" in balances["accounts"][0]
        assert "balance_eth" in balances["accounts"][0]

    return balances


@log_method
def test_get_normal_transactions():
    transactions = get_normal_transactions.invoke({
        "address": ethereum_address,
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert transactions is not None
    assert "success" in transactions
    if transactions["success"]:
        assert "transactions" in transactions
        assert "count" in transactions
        if transactions["count"] > 0:
            tx = transactions["transactions"][0]
            assert "hash" in tx

    return transactions


@log_method
def test_get_internal_transactions():
    transactions = get_internal_transactions.invoke({
        "address": ethereum_address,
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert transactions is not None
    assert "success" in transactions
    if transactions["success"] and transactions.get("count", 0) > 0:
        assert "internal_transactions" in transactions
        assert len(transactions["internal_transactions"]) > 0

    return transactions


@log_method
def test_get_erc20_token_transfers():
    transfers = get_erc20_token_transfers.invoke({
        "address": ethereum_address,
        "chain_id": chain_id,
        "contract_address": erc20_token_address,
        "page": 1,
        "offset": 5
    })
    assert transfers is not None
    assert "success" in transfers
    if transfers["success"] and transfers.get("count", 0) > 0:
        assert "erc20_transfers" in transfers
        assert len(transfers["erc20_transfers"]) > 0

    return transfers


@log_method
def test_get_erc721_token_transfers():
    transfers = get_erc721_token_transfers.invoke({
        "address": ethereum_address,
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert transfers is not None
    assert "success" in transfers
    if transfers["success"] and transfers.get("count", 0) > 0:
        assert "erc721_transfers" in transfers
        assert len(transfers["erc721_transfers"]) > 0

    return transfers


@log_method
def test_get_blocks_mined_by_address():
    blocks = get_blocks_mined_by_address.invoke({
        "address": ethereum_address,  # Note: This address may not have mined blocks
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert blocks is not None
    assert "success" in blocks
    # Even if no blocks are found, the API call should succeed

    return blocks

# === TRANSACTIONS METHODS TESTS ===


@log_method
def test_get_transaction_status():
    status = get_transaction_status.invoke({
        "txhash": ethereum_transaction_hash,
        "chain_id": chain_id
    })
    assert status is not None
    assert "success" in status
    if status["success"]:
        assert "transaction_status" in status

    return status


@log_method
def test_get_transaction_receipt_status():
    receipt = get_transaction_receipt_status.invoke({
        "txhash": ethereum_transaction_hash,
        "chain_id": chain_id
    })
    assert receipt is not None
    assert "success" in receipt
    if receipt["success"]:
        assert "receipt_status" in receipt
        assert receipt["receipt_status"] in [0, 1]
        assert "status_message" in receipt

    return receipt

# === BLOCKS METHODS TESTS ===


@log_method
def test_get_block_reward():
    reward = get_block_reward.invoke({
        "block_number": ethereum_block_number,
        "chain_id": chain_id
    })
    assert reward is not None
    assert "success" in reward
    if reward["success"]:
        assert "block_reward" in reward
        assert "blockNumber" in reward["block_reward"]

    return reward


@log_method
def test_get_estimated_block_time():
    block_time = get_estimated_block_time.invoke({
        "chain_id": chain_id
    })
    assert block_time is not None
    assert "success" in block_time
    if block_time["success"]:
        assert "estimated_block_time_seconds" in block_time
        assert isinstance(block_time["estimated_block_time_seconds"], int)
        assert block_time["estimated_block_time_seconds"] > 0

    return block_time

# === LOGS METHODS TESTS ===


@log_method
def test_get_logs():
    # Get the latest block number
    latest_block = get_latest_chain_block_number.invoke({
        "chain_id": chain_id
    })

    logs = get_logs.invoke({
        "address": erc20_token_address,
        "from_block": latest_block - 10000,
        "to_block": latest_block,
        "chain_id": chain_id,
        # Transfer event
        "topic0": "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    })
    assert logs is not None
    assert "success" in logs
    # The API may return no logs if there are none in the specified range

    return logs

# === GETH/PARITY PROXY METHODS TESTS ===


@log_method
def test_eth_block_number():
    block_number = eth_block_number.invoke({
        "chain_id": chain_id
    })
    assert block_number is not None
    assert "success" in block_number
    if block_number["success"]:
        assert "hex_block_number" in block_number
        assert "block_number" in block_number
        assert block_number["hex_block_number"].startswith("0x")
        assert isinstance(block_number["block_number"], int)

    return block_number


@log_method
def test_eth_get_block_by_number():
    block = eth_get_block_by_number.invoke({
        "block_number": "latest",
        "include_txs": False,
        "chain_id": chain_id
    })
    assert block is not None
    assert "success" in block
    if block["success"]:
        assert "block" in block
        assert "number" in block["block"]

    return block


@log_method
def test_eth_get_transaction_by_hash():
    transaction = eth_get_transaction_by_hash.invoke({
        "txhash": ethereum_transaction_hash,
        "chain_id": chain_id
    })
    assert transaction is not None
    assert "success" in transaction
    if transaction["success"]:
        assert "transaction" in transaction
        if transaction["transaction"]:
            assert "hash" in transaction["transaction"]
            assert transaction["transaction"]["hash"].lower(
            ) == ethereum_transaction_hash.lower()

    return transaction


@log_method
def test_eth_get_transaction_receipt():
    receipt = eth_get_transaction_receipt.invoke({
        "txhash": ethereum_transaction_hash,
        "chain_id": chain_id
    })
    assert receipt is not None
    assert "success" in receipt
    if receipt["success"]:
        assert "receipt" in receipt
        if receipt["receipt"]:
            assert "transactionHash" in receipt["receipt"]
            assert receipt["receipt"]["transactionHash"].lower(
            ) == ethereum_transaction_hash.lower()

    return receipt

# === TOKENS METHODS TESTS ===


@log_method
def test_get_token_supply():
    supply = get_token_supply.invoke({
        "contract_address": erc20_token_address,
        "chain_id": chain_id
    })
    assert supply is not None
    assert "success" in supply
    if supply["success"]:
        assert "raw_supply" in supply
        assert isinstance(supply["raw_supply"], int)
        if "formatted_supply" in supply:
            assert isinstance(supply["formatted_supply"], float)

    return supply


@log_method
def test_get_token_account_balance():
    balance = get_token_account_balance.invoke({
        "contract_address": erc20_token_address,
        "address": ethereum_address,
        "chain_id": chain_id
    })
    assert balance is not None
    assert "success" in balance
    if balance["success"]:
        assert "raw_balance" in balance
        assert isinstance(balance["raw_balance"], int)
        if "formatted_balance" in balance:
            assert isinstance(balance["formatted_balance"], float)

    return balance

# === GAS TRACKER METHODS TESTS ===


@log_method
def test_get_gas_oracle():
    gas_oracle = get_gas_oracle.invoke({
        "chain_id": chain_id
    })
    assert gas_oracle is not None
    assert "success" in gas_oracle
    if gas_oracle["success"]:
        assert "gas_oracle" in gas_oracle
        if gas_oracle["gas_oracle"]:
            assert "SafeGasPrice" in gas_oracle["gas_oracle"] or "suggestBaseFee" in gas_oracle["gas_oracle"]

    return gas_oracle

# === STATS METHODS TESTS ===


@log_method
def test_get_eth_price():
    price = get_eth_price.invoke({
        "chain_id": chain_id
    })
    assert price is not None
    assert "success" in price
    if price["success"]:
        assert "eth_price_usd" in price
        assert isinstance(price["eth_price_usd"], float)

    return price


@log_method
def test_get_eth_supply():
    supply = get_eth_supply.invoke({
        "chain_id": chain_id
    })
    assert supply is not None
    assert "success" in supply
    if supply["success"]:
        assert "supply_wei" in supply
        assert "supply_eth" in supply
        assert isinstance(supply["supply_wei"], int)
        assert isinstance(supply["supply_eth"], float)

    return supply


@log_method
def test_get_eth_daily_price():
    # Get data for the last 3 days
    today = datetime.datetime.now()
    end_date = today.strftime("%Y-%m-%d")
    start_date = (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")

    price_data = get_eth_daily_price.invoke({
        "chain_id": chain_id,
        "start_date": start_date,
        "end_date": end_date
    })
    assert price_data is not None
    assert "success" in price_data
    # Data may not be available for the most recent days

    return price_data

# === L2 DEPOSITS/WITHDRAWALS METHODS TESTS ===


@log_method
def test_get_l2_deposits():
    deposits = get_l2_deposits.invoke({
        "address": ethereum_address,
        "l2chain": "optimism",
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert deposits is not None
    assert "success" in deposits
    # The address may not have L2 deposits

    return deposits


@log_method
def test_get_l2_withdrawals():
    withdrawals = get_l2_withdrawals.invoke({
        "address": ethereum_address,
        "l2chain": "optimism",
        "chain_id": chain_id,
        "page": 1,
        "offset": 5
    })
    assert withdrawals is not None
    assert "success" in withdrawals
    # The address may not have L2 withdrawals

    return withdrawals

# === USAGE METHODS TESTS ===


@log_method
def test_get_daily_network_usage():
    # Get data for the last 3 days
    today = datetime.datetime.now()
    end_date = (today - datetime.timedelta(days=1)
                ).strftime("%Y-%m-%d")  # Yesterday
    start_date = (today - datetime.timedelta(days=4)
                  ).strftime("%Y-%m-%d")  # 4 days ago

    network_usage = get_daily_network_usage.invoke({
        "chain_id": chain_id,
        "start_date": start_date,
        "end_date": end_date
    })
    assert network_usage is not None
    assert "success" in network_usage
    # Data may not be available for the most recent days

    return network_usage


if __name__ == "__main__":
    # Existing tests
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

    # New tests for Account methods
    test_get_account_balance()
    test_get_multi_account_balance()
    test_get_normal_transactions()
    test_get_internal_transactions()
    test_get_erc20_token_transfers()
    test_get_erc721_token_transfers()
    test_get_blocks_mined_by_address()

    # Transaction methods
    test_get_transaction_status()
    test_get_transaction_receipt_status()

    # Block methods
    test_get_block_reward()
    test_get_estimated_block_time()

    # Logs methods
    test_get_logs()

    # Geth/Parity proxy methods
    test_eth_block_number()
    test_eth_get_block_by_number()
    test_eth_get_transaction_by_hash()
    test_eth_get_transaction_receipt()

    # Tokens methods
    test_get_token_supply()
    test_get_token_account_balance()

    # Gas tracker methods
    test_get_gas_oracle()

    # Stats methods
    test_get_eth_price()
    test_get_eth_supply()
    test_get_eth_daily_price()

    # L2 methods
    test_get_l2_deposits()
    test_get_l2_withdrawals()

    # Usage methods
    test_get_daily_network_usage()
