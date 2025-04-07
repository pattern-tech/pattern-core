"""
Provider tools for the agentflow module.

This package contains tools for interacting with various blockchain providers:
- Moralis: Tools for querying Moralis API for wallet data, token balances, and transactions
- ChainScan: Tools for interacting with blockchain explorers and smart contracts
- GoldRush: Tools for interacting with the GoldRush API
"""

# Moralis tools
from src.agentflow.providers.moralis_tools import (
    get_wallet_token_balances,
    get_wallet_stats,
    get_wallet_history,
    get_transaction_detail,
    get_token_approvals
)

# Chain scan tools
from src.agentflow.providers.chain_scan_tools import (
    get_contract_source_code,
    get_contract_abi,
    get_abi_of_event,
    get_contract_events,
    get_latest_chain_block_number,
    convert_timestamp_to_block_number,
    get_latest_eth_block_hash,
    get_block_transactions,
    call_contract_function,
    get_current_timestamp,
    convert_to_timestamp,
    decode_transaction_input
)

# For convenience, export all tools
__all__ = [
    # Moralis tools
    "get_wallet_token_balances",
    "get_wallet_stats",
    "get_wallet_history",
    "get_transaction_detail",
    "get_token_approvals",
    
    # Chain scan tools
    "get_contract_source_code",
    "get_contract_abi",
    "get_abi_of_event",
    "get_contract_events",
    "get_latest_chain_block_number",
    "convert_timestamp_to_block_number",
    "get_latest_eth_block_hash",
    "get_block_transactions",
    "call_contract_function",
    "get_current_timestamp",
    "convert_to_timestamp",
    "decode_transaction_input",

]
