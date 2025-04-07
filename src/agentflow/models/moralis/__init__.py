"""
Moralis models for Moralis API requests and responses.
"""

# Import all models from moralis_models.py
from src.agentflow.models.moralis.moralis_models import (
    # Input models
    TokenBalanceInput,
    WalletHistoryInput,
    WalletStatsInput,
    TransactionDetailInput,
    TokenApprovalInput,

    # Response models
    TokenBalanceResponse,
    WalletHistoryResponse,
    WalletStatsResponse,
    TransactionDetailResponse,
    TokenApprovalResponse,

    # Component models
    Transaction,
    TokenBalance,
    InternalTransaction,
    NFTTransfer,
    ERC20Transfer,
    NativeTransfer,
    WalletHistoryItem,
    TokenInfo,
    SpenderInfo,
    TokenApprovalItem
)

# Create convenient groupings
inputs = [
    TokenBalanceInput,
    WalletHistoryInput,
    WalletStatsInput,
    TransactionDetailInput,
    TokenApprovalInput
]

responses = [
    TokenBalanceResponse,
    WalletHistoryResponse,
    WalletStatsResponse,
    TransactionDetailResponse,
    TokenApprovalResponse
]

components = [
    Transaction,
    TokenBalance,
    InternalTransaction,
    NFTTransfer,
    ERC20Transfer,
    NativeTransfer,
    WalletHistoryItem,
    TokenInfo,
    SpenderInfo,
    TokenApprovalItem
]

# Export all models
__all__ = [
    # Input models
    "TokenBalanceInput",
    "WalletHistoryInput",
    "WalletStatsInput",
    "TransactionDetailInput",
    "TokenApprovalInput",

    # Response models
    "TokenBalanceResponse",
    "WalletHistoryResponse",
    "WalletStatsResponse",
    "TransactionDetailResponse",
    "TokenApprovalResponse",

    # Component models
    "Transaction",
    "TokenBalance",
    "InternalTransaction",
    "NFTTransfer",
    "ERC20Transfer",
    "NativeTransfer",
    "WalletHistoryItem",
    "TokenInfo",
    "SpenderInfo",
    "TokenApprovalItem"
]
