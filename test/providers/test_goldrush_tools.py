import pytest
from unittest import mock
import json
import functools
from src.agentflow.providers.goldrush_tools import (
    get_wallet_activity,
    get_balance_for_address,
    get_wallet_transactions,
    get_transactions_summary,
    get_transaction_detail,
    get_token_approvals
)


def test_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Running function: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Execution completed. Result: {result}")
        return result
    return wrapper


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
        self.text = json.dumps(json_data)

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP Error: {self.status_code}")
        return None


@pytest.fixture
def mock_call_goldrush_api():
    with mock.patch("src.agentflow.providers.goldrush_tools._call_goldrush_api") as mock_api:
        # Configure mock for wallet activity
        mock_api.side_effect = lambda url, params=None: {
            # For get_wallet_activity
            "/v1/address/": {
                "data": {
                    "items": [
                        {
                            "name": "Ethereum",
                            "chain_id": "1",
                            "is_testnet": False,
                            "label": "eth-mainnet",
                            "category_label": "EVM",
                            "logo_url": "https://example.com/logo.png",
                            "last_seen_at": "2023-01-01T00:00:00Z"
                        }
                    ]
                }
            },
            # For get_balance_for_address
            "/v1/eth-mainnet/address/": {
                "data": {
                    "items": [
                        {
                            "contract_decimals": 18,
                            "contract_name": "Ethereum",
                            "contract_ticker_symbol": "ETH",
                            "contract_address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
                            "contract_display_name": "Ethereum",
                            "logo_url": "https://example.com/eth-logo.png",
                            "last_transferred_at": "2023-01-01T00:00:00Z",
                            "native_token": True,
                            "type": "cryptocurrency",
                            "balance": "1000000000000000000",
                            "quote_rate": 2000.00,
                            "quote": 2000.00
                        }
                    ]
                }
            },
            # For get_wallet_transactions
            "/v1/eth-mainnet/address/": {
                "data": {
                    "items": [
                        {
                            "block_signed_at": "2023-01-01T00:00:00Z",
                            "block_height": 12345678,
                            "tx_hash": "0xabcdef1234567890",
                            "successful": True,
                            "from_address": "0x1234",
                            "to_address": "0x5678",
                            "value": "1000000000000000000",
                            "value_quote": 2000.00,
                            "gas_offered": 21000,
                            "gas_spent": 21000,
                            "gas_price": 20000000000,
                            "fees_paid": "0.00042"
                        }
                    ]
                }
            },
            # For get_transactions_summary
            "/v1/eth-mainnet/address/": {
                "data": {
                    "items": {
                        "earliest_transaction": {
                            "block_height": 12340000,
                            "block_signed_at": "2022-01-01T00:00:00Z",
                            "tx_hash": "0xaaaa"
                        },
                        "latest_transaction": {
                            "block_height": 12345678,
                            "block_signed_at": "2023-01-01T00:00:00Z",
                            "tx_hash": "0xbbbb"
                        }
                    }
                }
            },
            # For get_transaction_detail
            "/v1/eth-mainnet/transaction_v2/": {
                "data": {
                    "items": [
                        {
                            "block_signed_at": "2023-01-01T00:00:00Z",
                            "block_height": 12345678,
                            "tx_hash": "0xabcdef1234567890",
                            "successful": True,
                            "from_address": "0x1234",
                            "to_address": "0x5678",
                            "value": "1000000000000000000",
                            "input_data": "0x",
                            "log_events": []
                        }
                    ]
                }
            },
            # For get_token_approvals
            "/v1/eth-mainnet/approvals/": {
                "data": {
                    "items": [
                        {
                            "token_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
                            "ticker_symbol": "USDT",
                            "contract_decimals": 6,
                            "logo_url": "https://example.com/logo.png",
                            "quote_rate": 1.0,
                            "balance": "1000000",
                            "balance_quote": 1.0,
                            "spenders": [
                                {
                                    "address": "0x1234",
                                    "allowance": "10000000000"
                                }
                            ]
                        }
                    ]
                }
            }
        }.get(next((sub for sub in url.split("/") if sub.startswith("eth") or sub == "address"), ""), {})

        yield mock_api


@test_decorator
def test_get_wallet_activity(mock_call_goldrush_api):
    """Test the get_wallet_activity tool function."""
    result = get_wallet_activity(
        wallet_address="0x123456789abcdef",
        output_include=["name", "chain_id", "is_testnet"]
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]
    assert "chain_id" in result[0]
    assert "is_testnet" in result[0]


@test_decorator
def test_get_balance_for_address(mock_call_goldrush_api):
    """Test the get_balance_for_address tool function."""
    result = get_balance_for_address(
        wallet_address="0x123456789abcdef",
        output_include=["contract_decimals", "contract_name",
                        "contract_ticker_symbol", "balance"]
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert "contract_decimals" in result[0]
    assert "contract_name" in result[0]
    assert "contract_ticker_symbol" in result[0]
    assert "balance" in result[0]


@test_decorator
def test_get_wallet_transactions(mock_call_goldrush_api):
    """Test the get_wallet_transactions tool function."""
    result = get_wallet_transactions(
        wallet_address="0x123456789abcdef",
        output_include=["block_signed_at",
                        "tx_hash", "from_address", "to_address"],
        page=0
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert "block_signed_at" in result[0]
    assert "tx_hash" in result[0]
    assert "from_address" in result[0]
    assert "to_address" in result[0]


@test_decorator
def test_get_transactions_summary(mock_call_goldrush_api):
    """Test the get_transactions_summary tool function."""
    result = get_transactions_summary(
        wallet_address="0x123456789abcdef"
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, dict)
    assert "earliest_transaction" in result
    assert "latest_transaction" in result
    assert "block_height" in result["earliest_transaction"]
    assert "tx_hash" in result["latest_transaction"]


@test_decorator
def test_get_transaction_detail(mock_call_goldrush_api):
    """Test the get_transaction_detail tool function."""
    result = get_transaction_detail(
        tx_hash="0xabcdef1234567890",
        output_include=["block_signed_at",
                        "tx_hash", "from_address", "to_address"]
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert "block_signed_at" in result[0]
    assert "tx_hash" in result[0]
    assert "from_address" in result[0]
    assert "to_address" in result[0]


@test_decorator
def test_get_token_approvals(mock_call_goldrush_api):
    """Test the get_token_approvals tool function."""
    result = get_token_approvals(
        wallet_address="0x123456789abcdef",
        output_include=["token_address", "ticker_symbol", "contract_decimals"]
    )

    # Verify the API was called
    mock_call_goldrush_api.assert_called_once()

    # Check result structure
    assert isinstance(result, list)
    assert len(result) > 0
    assert "token_address" in result[0]
    assert "ticker_symbol" in result[0]
    assert "contract_decimals" in result[0]
