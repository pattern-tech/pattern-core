"""
Chain scan models for blockchain explorer and smart contract interactions.
"""

# Import all models from chain_scan_models.py
from src.agentflow.models.chain_scan.chain_scan_models import (
    # Input models
    ContractAbiInput,
    ContractSourceCodeInput,
    EventAbiInput,
    TimestampToBlockNumberInput,
    ConvertToTimestampInput,
    EventAbiOfContractInput,
    ContractEventsInput,
    LatestBlockNumberInput,
    LatestBlockHashInput,
    BlockTransactionsInput,
    ContractFunctionCallInput,
    DecodeTransactionInput,

    # Response models
    ContractAbiResponse,
    ContractSourceCodeResponse,
    EventAbiResponse,
    BlockNumberResponse,
    TimestampResponse,
    ContractEventsResponse,
    BlockHashResponse,
    BlockTransactionsResponse,
    ContractFunctionCallResponse,
    CurrentTimestampResponse,
    DecodeTransactionResponse
)

# Create convenient groupings
inputs = [
    ContractAbiInput,
    ContractSourceCodeInput,
    EventAbiInput,
    TimestampToBlockNumberInput,
    ConvertToTimestampInput,
    EventAbiOfContractInput,
    ContractEventsInput,
    LatestBlockNumberInput,
    LatestBlockHashInput,
    BlockTransactionsInput,
    ContractFunctionCallInput,
    DecodeTransactionInput
]

responses = [
    ContractAbiResponse,
    ContractSourceCodeResponse,
    EventAbiResponse,
    BlockNumberResponse,
    TimestampResponse,
    ContractEventsResponse,
    BlockHashResponse,
    BlockTransactionsResponse,
    ContractFunctionCallResponse,
    CurrentTimestampResponse,
    DecodeTransactionResponse
]

# Export all models
__all__ = [
    # Input models
    "ContractAbiInput",
    "ContractSourceCodeInput",
    "EventAbiInput",
    "TimestampToBlockNumberInput",
    "ConvertToTimestampInput",
    "EventAbiOfContractInput",
    "ContractEventsInput",
    "LatestBlockNumberInput",
    "LatestBlockHashInput",
    "BlockTransactionsInput",
    "ContractFunctionCallInput",
    "DecodeTransactionInput",

    # Response models
    "ContractAbiResponse",
    "ContractSourceCodeResponse",
    "EventAbiResponse",
    "BlockNumberResponse",
    "TimestampResponse",
    "ContractEventsResponse",
    "BlockHashResponse",
    "BlockTransactionsResponse",
    "ContractFunctionCallResponse",
    "CurrentTimestampResponse",
    "DecodeTransactionResponse"
]
