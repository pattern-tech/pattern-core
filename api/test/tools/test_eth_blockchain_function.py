import unittest

from src.agent.tools.all.eth_blockchain_function import (
    get_current_timestamp,
    convert_to_timestamp,
    get_contract_source_code,
    get_contract_abi,
    get_abi_of_event,
    get_contract_events,
    get_latest_eth_block_number,
    convert_timestamp_to_block_number,
    get_balance_for_address
)


class TestEthBlockchainFunction(unittest.TestCase):

    VALID_CONTRACT_ADDRESS = "0x06012c8cf97bead5deae237070f9587f8e7a266d"
    VALID_WALLET_ADDRESS = "0xba4bac5bd6ab7c4fda3eadb2f9fc5ba8b5b60c23"
    INVALID_WALLET_ADDRESS = INVALID_CONTRACT_ADDRESS = "0x..."

    def test_get_current_timestamp(self):
        ts = get_current_timestamp.invoke(input={})
        self.assertIsInstance(ts, int)

    def test_convert_to_timestamp_valid(self):
        ts = convert_to_timestamp.invoke(input={"date_str": "January 1, 2020"})
        self.assertIsInstance(ts, int)

    def test_convert_to_timestamp_invalid(self):
        ts = convert_to_timestamp.invoke(
            input={"date_str": "not a valid date string"})
        self.assertIn("Could not parse the date string", ts)

    def test_get_contract_source_code_valid_contract(self):
        source_code = get_contract_source_code.invoke(
            input={"contract_address": self.VALID_CONTRACT_ADDRESS}
        )
        self.assertIn(
            "The Ownable constructor sets the original `owner` of the contract",
            source_code,
        )

    def test_get_contract_source_code_invalid_contract(self):
        source_code = get_contract_source_code.invoke(
            input={"contract_address": self.INVALID_CONTRACT_ADDRESS}
        )
        self.assertIn("string indices must be integers", source_code)

    def test_contract_abi_valid_contract(self):
        abi = get_contract_abi.invoke(
            input={"contract_address": self.VALID_CONTRACT_ADDRESS}
        )
        self.assertIsInstance(abi, list)
        self.assertIn("Approval", str(abi))

    def test_contract_abi_invalid_contract(self):
        abi = get_contract_abi.invoke(
            input={"contract_address": self.INVALID_CONTRACT_ADDRESS}
        )
        self.assertIn("JSONDecodeError", abi)

    def test_get_abi_of_event_valid_contract(self):
        abi_event = get_abi_of_event.invoke(
            input={
                "contract_address": self.VALID_CONTRACT_ADDRESS,
                "event_name": "Approval",
            }
        )
        self.assertIsInstance(abi_event, dict)
        self.assertIsInstance(abi_event.get("inputs"), list)

    def test_get_abi_of_event_valid_contract(self):
        abi_event = get_abi_of_event.invoke(
            input={
                "contract_address": self.VALID_CONTRACT_ADDRESS,
                "event_name": "Approval",
            }
        )
        self.assertIsInstance(abi_event, dict)
        self.assertIsInstance(abi_event.get("inputs"), list)

    def test_get_contract_events_invalid_contract(self):
        events = get_contract_events.invoke(
            input={"contract_address": self.INVALID_CONTRACT_ADDRESS,
                   "event_name": "Approvals"}
        )
        self.assertIn("JSONDecodeError", events)

    def test_get_latest_eth_block_number(self):
        block_number = get_latest_eth_block_number.invoke(input={})
        self.assertIsInstance(block_number, int)

    def test_convert_timestamp_to_block_number(self):
        block_number = convert_timestamp_to_block_number.invoke(
            input={"timestamp": 1611168000}
        )
        self.assertEqual(int(block_number), 11694042)

    # TODO: test case for get balance method


if __name__ == "__main__":
    unittest.main()
