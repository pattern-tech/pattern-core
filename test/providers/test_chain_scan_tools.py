import pytest
import time
from unittest import mock
import json
import functools
from datetime import datetime
from src.agentflow.providers.chain_scan_tools import (
    get_current_timestamp,
    convert_to_timestamp,
    get_contract_source_code,
    get_contract_abi,
    get_abi_of_event,
    get_contract_events,
    get_latest_chain_block_number,
    convert_timestamp_to_block_number,
    get_latest_eth_block_hash,
    get_block_transactions,
    decode_transaction_input,
    call_contract_function
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
def mock_requests_get(monkeypatch):
    def _mock_get(*args, **kwargs):
        params = kwargs.get('params', {})
        action = params.get('action', '')

        if action == 'getabi':
            return MockResponse({
                "status": "1",
                "message": "OK",
                "result": json.dumps([
                    {
                        "inputs": [],
                        "name": "totalSupply",
                        "outputs": [{"type": "uint256", "name": ""}],
                        "stateMutability": "view",
                        "type": "function"
                    },
                    {
                        "anonymous": False,
                        "inputs": [
                            {"indexed": True, "name": "from", "type": "address"},
                            {"indexed": True, "name": "to", "type": "address"},
                            {"indexed": False, "name": "value", "type": "uint256"}
                        ],
                        "name": "Transfer",
                        "type": "event"
                    }
                ])
            })
        elif action == 'getsourcecode':
            return MockResponse({
                "status": "1",
                "message": "OK",
                "result": [{
                    "SourceCode": "contract Token { ... }",
                    "ABI": json.dumps([
                        {
                            "inputs": [],
                            "name": "totalSupply",
                            "outputs": [{"type": "uint256", "name": ""}],
                            "stateMutability": "view",
                            "type": "function"
                        }
                    ]),
                    "ContractName": "Token",
                    "Implementation": "0x0000000000000000000000000000000000000000",
                    "Proxy": "0"
                }]
            })
        elif action == 'getblocknobytime':
            return MockResponse({
                "status": "1",
                "message": "OK",
                "result": "15000000"
            })

        return MockResponse({
            "status": "1",
            "message": "OK",
            "result": "mock data"
        })

    monkeypatch.setattr('requests.get', _mock_get)
    return _mock_get


@pytest.fixture
def mock_web3():
    with mock.patch('src.agentflow.providers.chain_scan_tools.Web3') as mock_web3_class:
        # Mock the HTTPProvider
        mock_provider = mock.MagicMock()
        mock_web3_class.HTTPProvider.return_value = mock_provider

        # Mock the Web3 instance
        mock_web3_instance = mock.MagicMock()
        mock_web3_class.return_value = mock_web3_instance

        # Mock eth properties
        mock_eth = mock.MagicMock()
        mock_web3_instance.eth = mock_eth
        mock_eth.block_number = 16000000

        # Mock contract
        mock_contract = mock.MagicMock()
        mock_eth.contract.return_value = mock_contract

        # Mock events property on contract
        mock_events = mock.MagicMock()
        mock_contract.events = mock_events

        # Mock a specific event
        mock_event = mock.MagicMock()
        mock_events.Transfer = mock.MagicMock(return_value=mock_event)

        # Mock get_logs method on the event instance
        mock_event.return_value.get_logs.return_value = [
            {
                'address': '0x1234567890123456789012345678901234567890',
                'topics': ['0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'],
                'data': '0x0000000000000000000000000000000000000000000000000de0b6b3a7640000',
                'blockNumber': 15000000,
                'transactionHash': '0xabcdef1234567890abcdef1234567890',
                'logIndex': 0
            }
        ]

        # Mock get_block
        mock_eth.get_block.return_value = mock.MagicMock(
            hash=b'block_hash_bytes',
            transactions=[
                {
                    'hash': '0xabcdef1234567890',
                    'from': '0x1234567890123456789012345678901234567890',
                    'to': '0x0987654321098765432109876543210987654321',
                    'value': 1000000000000000000,  # 1 ETH
                    'gas': 21000,
                    'gasPrice': 20000000000
                }
            ]
        )

        # Mock to_hex, keccak and from_wei methods
        mock_web3_class.to_hex.return_value = '0xabcdef'
        mock_web3_class.keccak.return_value = b'0xabcdef1234567890'
        mock_web3_class.from_wei.return_value = 1.0

        # Mock decode_function_input
        mock_contract.decode_function_input.return_value = (
            mock.MagicMock(
                fn_name='transfer',
                abi={'inputs': [{'name': 'to', 'type': 'address'}, {
                    'name': 'value', 'type': 'uint256'}]}
            ),
            {'to': '0x1234567890123456789012345678901234567890',
                'value': 1000000000000000000}
        )

        # Mock function call
        mock_function = mock.MagicMock()
        mock_contract.functions.totalSupply.return_value = mock_function
        mock_function.call.return_value = 1000000000000000000000000  # 1M tokens

        yield mock_web3_class


@test_decorator
def test_get_current_timestamp():
    """Test the get_current_timestamp tool function."""
    # Get timestamp before and after function call
    before = int(time.time())
    result = get_current_timestamp()
    after = int(time.time())

    # Timestamp should be between before and after
    assert isinstance(result, int)
    assert before <= result <= after


@test_decorator
def test_convert_to_timestamp():
    """Test the convert_to_timestamp tool function."""
    # Test with specific date
    result = convert_to_timestamp("2023-01-01")

    # Expected timestamp for 2023-01-01 00:00:00 UTC
    expected = int(datetime(2023, 1, 1).timestamp())

    assert isinstance(result, int)
    assert result == expected

    # Test with relative time
    result = convert_to_timestamp("1 day ago")
    now = int(time.time())
    one_day_seconds = 24 * 60 * 60

    assert isinstance(result, int)
    assert now - one_day_seconds - 60 <= result <= now - \
        one_day_seconds + 60  # Allow 1 minute variation


@test_decorator
def test_get_contract_source_code(mock_requests_get, mock_web3):
    """Test the get_contract_source_code tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        result = get_contract_source_code(
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id="1"
        )

        assert isinstance(result, dict)
        assert "proxy" in result
        assert "implementation" in result
        assert isinstance(result["implementation"], list)
        assert len(result["implementation"]) > 0


@test_decorator
def test_get_contract_abi(mock_requests_get, mock_web3):
    """Test the get_contract_abi tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        result = get_contract_abi(
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id="1"
        )

        assert isinstance(result, dict)
        assert "proxy" in result
        assert "implementation" in result
        assert isinstance(result["implementation"], list)
        assert len(result["implementation"]) > 0


@test_decorator
def test_get_abi_of_event(mock_requests_get, mock_web3):
    """Test the get_abi_of_event tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        result = get_abi_of_event(
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id="1",
            event_name="Transfer"
        )

        assert isinstance(result, dict)
        assert result["name"] == "Transfer"
        assert result["type"] == "event"
        assert isinstance(result["inputs"], list)
        assert len(result["inputs"]) > 0


@test_decorator
def test_get_contract_events(mock_requests_get, mock_web3):
    """Test the get_contract_events tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        result = get_contract_events(
            contract_address="0x1234567890123456789012345678901234567890",
            chain_id="1",
            event_name="Transfer"
        )

        assert isinstance(result, list)
        assert len(result) > 0
        assert "blockNumber" in result[0]
        assert "transactionHash" in result[0]


@test_decorator
def test_get_latest_chain_block_number(mock_web3):
    """Test the get_latest_chain_block_number tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
    }):
        result = get_latest_chain_block_number(chain_id="1")

        assert isinstance(result, int)
        assert result == 16000000  # From our mock


@test_decorator
def test_convert_timestamp_to_block_number(mock_requests_get, mock_web3):
    """Test the convert_timestamp_to_block_number tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        result = convert_timestamp_to_block_number(
            timestamp=1672531200,  # 2023-01-01 00:00:00 UTC
            chain_id="1"
        )

        assert isinstance(result, int)
        assert result == 15000000  # From our mock


@test_decorator
def test_get_latest_eth_block_hash(mock_web3):
    """Test the get_latest_eth_block_hash tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key'
    }):
        result = get_latest_eth_block_hash(chain_id="1")

        assert isinstance(result, str)
        assert result == "0xabcdef"  # From our mock


@test_decorator
def test_get_block_transactions(mock_web3):
    """Test the get_block_transactions tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key'
    }):
        result = get_block_transactions(
            block_number=15000000,
            chain_id="1",
            output_include=["hash", "from", "to", "value"]
        )

        # Result is a string representation of list because of JSON limitations
        assert isinstance(result, str)
        assert "0xabcdef1234567890" in result  # Transaction hash from our mock


@test_decorator
def test_decode_transaction_input(mock_web3):
    """Test the decode_transaction_input tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        with mock.patch("src.agentflow.providers.chain_scan_tools.get_contract_abi") as mock_get_abi:
            mock_get_abi.return_value = [
                {
                    "inputs": [
                        {"name": "to", "type": "address"},
                        {"name": "value", "type": "uint256"}
                    ],
                    "name": "transfer",
                    "outputs": [{"type": "bool", "name": ""}],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]

            result = decode_transaction_input(
                transaction_input="0xa9059cbb0000000000000000000000001234567890123456789012345678901234567890000000000000000000000000000000000000000000000000de0b6b3a7640000",
                contract_address="0x1234567890123456789012345678901234567890",
                chain_id="1"
            )

            assert isinstance(result, dict)
            assert "function_name" in result
            assert result["function_name"] == "transfer"
            assert "parameters" in result
            assert len(result["parameters"]) == 2


@test_decorator
def test_call_contract_function(mock_web3):
    """Test the call_contract_function tool function."""
    # Mock the environment variables
    with mock.patch.dict('os.environ', {
        'ETH_RPC': 'https://eth-mainnet.g.alchemy.com/v2/your-api-key',
        'ETHER_SCAN_API_KEY': 'YOUR_API_KEY'
    }):
        with mock.patch("src.agentflow.providers.chain_scan_tools.fetch_contract_source_code") as mock_source_code:
            mock_source_code.return_value = {
                "Proxy": "0",
                "ABI": json.dumps([
                    {
                        "inputs": [],
                        "name": "totalSupply",
                        "outputs": [{"type": "uint256", "name": ""}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ])
            }

            with mock.patch("src.agentflow.providers.chain_scan_tools.fetch_contract_abi") as mock_abi:
                mock_abi.return_value = [
                    {
                        "inputs": [],
                        "name": "totalSupply",
                        "outputs": [{"type": "uint256", "name": ""}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]

                result = call_contract_function(
                    contract_address="0x1234567890123456789012345678901234567890",
                    chain_id="1",
                    function_name="totalSupply"
                )

                assert isinstance(result, dict)
                assert "success" in result
                assert result["success"] is True
                assert "result" in result
