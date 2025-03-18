from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field

# Pydantic models for function inputs
class WalletActiveChainInput(BaseModel):
    """Input model for get_wallet_active_chains function.
    Get the active chains for a wallet address.
    """
    wallet_address: str = Field(..., description="Ethereum wallet address")
    chains: Optional[List[str]] = Field(None, description="The chains to query. If left empty, defaults to all chains supported by Moralis.")


class TokenBalanceInput(BaseModel):
    """Input model for get_wallet_token_balances function.
    Get token balances for a specific wallet address and their token prices in USD (paginated).
    Apply decimal conversion for balance.
    """
    wallet_address: str = Field(..., description="Ethereum wallet address")
    cursor: Optional[str] = Field(None, description="The cursor returned in the previous response (used for getting the next page). End of page cursor is None")


class WalletStatsInput(BaseModel):
    """Input model for get_wallet_stats function.
    Get the stats for a wallet address.
    """
    wallet_address: str = Field(..., description="Ethereum wallet address")


class WalletHistoryInput(BaseModel):
    """Input model for get_wallet_history function.
    Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers
    and contract interactions (paginated & in descending order).
    """
    wallet_address: str = Field(..., description="Ethereum wallet address")
    cursor: Optional[str] = Field(None, description="The cursor returned in the previous response (used for getting the next page). End of page cursor is None")


class TransactionDetailInput(BaseModel):
    """Input model for get_transaction_detail function.
    Get the contents of a transaction by the given transaction hash.
    """
    transaction_hash: str = Field(..., description="Transaction hash to be decoded")


class TokenApprovalInput(BaseModel):
    """Input model for get_token_approvals function.
    Get ERC20 approvals for one or many wallet addresses and/or contract addresses, ordered by block number in descending order.
    """
    wallet_address: str = Field(..., description="Ethereum wallet address")
    cursor: Optional[str] = Field(None, description="The cursor returned in the previous response (used for getting the next page). End of page cursor is None")


# Pydantic models for Moralis API responses
class Transaction(BaseModel):
    """
    Represents a blockchain transaction with block information and hash.
    """
    block_number: Optional[str] = Field(None, description="The block number of the transaction")
    block_timestamp: Optional[str] = Field(None, description="The timestamp of the block in ISO format (e.g., '2022-08-23T20:58:31.000Z')")
    transaction_hash: Optional[str] = Field(None, description="The transaction hash")


class WalletActiveChain(BaseModel):
    """
    Represents an active blockchain for a wallet with first and last transaction details.
    """
    chain: Optional[str] = Field(None, description="The chain name (e.g., 'eth')")
    chain_id: Optional[str] = Field(None, description="The chain id in hexadecimal format (e.g., '0x1')")
    first_transaction: Optional[Transaction] = Field(None, description="The first transaction details including block number, timestamp and transaction hash")
    last_transaction: Optional[Transaction] = Field(None, description="The last transaction details including block number, timestamp and transaction hash")


class TokenBalance(BaseModel):
    token_address: Optional[str] = None
    symbol: Optional[str] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    thumbnail: Optional[str] = None
    decimals: Optional[int] = None
    balance: Optional[str] = None
    balance_formatted: Optional[str] = None
    usd_price: Optional[float] = None
    usd_price_24hr_percent_change: Optional[float] = None
    usd_price_24hr_usd_change: Optional[float] = None
    usd_value: Optional[float] = None
    usd_value_24hr_usd_change: Optional[float] = None
    native_token: Optional[bool] = None
    portfolio_percentage: Optional[float] = None


class TokenBalanceResponse(BaseModel):
    cursor: Optional[str] = None
    results: List[TokenBalance] = Field(default_factory=list)


class WalletStats(BaseModel):
    nfts: Optional[int] = None
    collections: Optional[int] = None
    transactions: Optional[int] = None
    nft_transfers: Optional[int] = None
    token_transfers: Optional[int] = None


class WalletHistoryItem(BaseModel):
    hash: Optional[str] = None
    from_address_entity: Optional[str] = None
    from_address_entity_logo: Optional[str] = None
    from_address: Optional[str] = None
    from_address_label: Optional[str] = None
    to_address_entity: Optional[str] = None
    to_address_entity_logo: Optional[str] = None
    to_address: Optional[str] = None
    to_address_label: Optional[str] = None
    value: Optional[str] = None
    receipt_contract_address: Optional[str] = None
    block_timestamp: Optional[str] = None
    block_number: Optional[str] = None
    block_hash: Optional[str] = None
    internal_transactions: Optional[Any] = None
    nft_transfers: Optional[Any] = None
    erc20_transfer: Optional[Any] = None
    native_transfers: Optional[Any] = None


class WalletHistoryResponse(BaseModel):
    cursor: Optional[str] = None
    results: List[WalletHistoryItem] = Field(default_factory=list)


class TransactionDetail(BaseModel):
    hash: Optional[str] = None
    from_address_entity: Optional[str] = None
    from_address_entity_logo: Optional[str] = None
    from_address: Optional[str] = None
    from_address_label: Optional[str] = None
    to_address_entity: Optional[str] = None
    to_address_entity_logo: Optional[str] = None
    to_address: Optional[str] = None
    to_address_label: Optional[str] = None
    value: Optional[str] = None
    receipt_gas_used: Optional[str] = None
    receipt_contract_address: Optional[str] = None
    receipt_root: Optional[str] = None
    receipt_status: Optional[str] = None
    block_timestamp: Optional[str] = None
    block_number: Optional[str] = None
    block_hash: Optional[str] = None
    decoded_call: Optional[Any] = None
    decoded_event: Optional[Any] = None


class TokenApproval(BaseModel):
    block_number: Optional[str] = None
    block_timestamp: Optional[str] = None
    transaction_hash: Optional[str] = None
    value: Optional[str] = None
    value_formatted: Optional[str] = None
    token: Optional[Dict[str, Any]] = None
    spender: Optional[Dict[str, Any]] = None


class TokenApprovalResponse(BaseModel):
    cursor: Optional[str] = None
    results: List[TokenApproval] = Field(default_factory=list)
