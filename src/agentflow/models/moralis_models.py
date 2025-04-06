from typing import Any, List, Optional, Dict, Literal
from pydantic import BaseModel, Field

# Pydantic models for function inputs


class TokenBalanceInput(BaseModel):
    """Input model for get_wallet_token_balances function.
    Get token balances for a specific wallet address and their token prices in USD (paginated).
    Apply decimal conversion for balance.
    """
    wallet_address: str = Field(..., description="Wallet address")
    chain: Literal[
        "eth", "0x1",           # Ethereum
        "polygon", "0x89",      # Polygon
        "bsc", "0x38",          # Binance Smart Chain
        "avalanche", "0xa86a",  # Avalanche
        "fantom", "0xfa",       # Fantom
        "palm", "0x2a15c308d",  # Palm
        "cronos", "0x19",       # Cronos
        "arbitrum", "0xa4b1",   # Arbitrum
        "chiliz", "0x15b38",    # Chiliz
        "gnosis", "0x64",       # Gnosis
        "base", "0x2105",       # Base
        "optimism", "0xa",      # Optimism
        "linea", "0xe708",      # Linea
        "moonbeam", "0x504",    # Moonbeam
        "moonriver", "0x505",   # Moonriver
        "flow", "0x2eb",        # Flow
        "ronin", "0x7e4",       # Ronin
        "lisk", "0x46f",        # Lisk
        "pulse", "0x171"        # Pulse
    ] = Field("eth", description="The blockchain to query. Can be specified by chain name or chain ID.")
    token_addresses: Optional[List[str]] = Field(
        None, description="The addresses of specific tokens to get balances for")
    exclude_spam: Optional[bool] = Field(
        None, description="Exclude spam tokens from the response")
    exclude_native: Optional[bool] = Field(
        None, description="Exclude native tokens from the response")
    cursor: Optional[str] = Field(
        None, description="The cursor returned in the previous response (used for getting the next page). End of page cursor is None")
    limit: Optional[int] = Field(
        None, description="The number of token balances to return (max 100)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class WalletHistoryInput(BaseModel):
    """Input model for get_wallet_history function.
    Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers
    and contract interactions (paginated & in descending order).
    """
    wallet_address: str = Field(..., description="wallet address")
    chain: Literal[
        "eth", "0x1",           # Ethereum
        "polygon", "0x89",      # Polygon
        "bsc", "0x38",          # Binance Smart Chain
        "avalanche", "0xa86a",  # Avalanche
        "fantom", "0xfa",       # Fantom
        "palm", "0x2a15c308d",  # Palm
        "cronos", "0x19",       # Cronos
        "arbitrum", "0xa4b1",   # Arbitrum
        "chiliz", "0x15b38",    # Chiliz
        "gnosis", "0x64",       # Gnosis
        "base", "0x2105",       # Base
        "optimism", "0xa",      # Optimism
        "linea", "0xe708",      # Linea
        "moonbeam", "0x504",    # Moonbeam
        "moonriver", "0x505",   # Moonriver
        "flow", "0x2eb",        # Flow
        "ronin", "0x7e4",       # Ronin
        "lisk", "0x46f",        # Lisk
        "pulse", "0x171"        # Pulse
    ] = Field("eth", description="The blockchain to query. Can be specified by chain name or chain ID.")
    from_block: Optional[int] = Field(
        None, description="The minimum block number from which to get the transactions")
    to_block: Optional[int] = Field(
        None, description="The maximum block number from which to get the transactions")
    from_date: Optional[str] = Field(
        None, description="The date from which to get the transactions in ISO format (e.g., '2023-06-05T00:00:00.000Z')")
    to_date: Optional[str] = Field(
        None, description="The date up to which to get the transactions in ISO format (e.g., '2023-06-05T00:00:00.000Z')")
    limit: Optional[int] = Field(
        None, description="The number of transactions to return (max 100)")
    cursor: Optional[str] = Field(
        None, description="The cursor returned in the previous response (used for getting the next page). End of page cursor is None")
    order: Literal["ASC", "DESC"] = Field(
        "DESC", description="The order in which to return the transactions.")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


# Pydantic models for Moralis API responses
class Transaction(BaseModel):
    """
    Represents a blockchain transaction with block information and hash.
    """
    block_number: Optional[str] = Field(
        None, description="The block number of the transaction")
    block_timestamp: Optional[str] = Field(
        None, description="The timestamp of the block in ISO format (e.g., '2022-08-23T20:58:31.000Z')")
    transaction_hash: Optional[str] = Field(
        None, description="The transaction hash")


class TokenBalance(BaseModel):
    """Represents a token balance with price information."""
    token_address: Optional[str] = Field(
        None, description="Address of the token contract")
    symbol: Optional[str] = Field(None, description="Symbol of the token")
    name: Optional[str] = Field(None, description="Name of the token")
    logo: Optional[str] = Field(None, description="URL to the token logo")
    thumbnail: Optional[str] = Field(
        None, description="URL to the token thumbnail")
    decimals: Optional[int] = Field(
        None, description="Number of decimal places for the token")
    balance: Optional[str] = Field(
        None, description="Raw balance in the token's smallest unit")
    balance_formatted: Optional[str] = Field(
        None, description="Formatted balance with decimal places applied")
    possible_spam: Optional[bool] = Field(
        None, description="Indicator if the token might be spam")
    verified_contract: Optional[bool] = Field(
        None, description="Indicator if the token contract is verified")
    usd_price: Optional[float] = Field(
        None, description="Current price of the token in USD")
    usd_price_24hr_percent_change: Optional[float] = Field(
        None, description="24-hour percent change in USD price")
    usd_price_24hr_usd_change: Optional[float] = Field(
        None, description="24-hour absolute change in USD price")
    usd_value: Optional[float] = Field(
        None, description="Total value of the token balance in USD")
    usd_value_24hr_usd_change: Optional[float] = Field(
        None, description="24-hour change in USD value of the token balance")
    native_token: Optional[bool] = Field(
        None, description="Indicator if this is the chain's native token")
    portfolio_percentage: Optional[float] = Field(
        None, description="Percentage of the wallet's portfolio this token represents")


class TokenBalanceResponse(BaseModel):
    """Response model for wallet token balances endpoint."""
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(
        None, description="Number of results per page")
    result: List[TokenBalance] = Field(
        default_factory=list, description="List of token balances")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class InternalTransaction(BaseModel):
    """Represents an internal transaction within a blockchain transaction."""
    transaction_hash: Optional[str] = Field(
        None, description="Transaction hash of the internal transaction")
    block_number: Optional[str] = Field(
        None, description="Block number where this internal transaction occurred")
    block_hash: Optional[str] = Field(
        None, description="Block hash where this internal transaction occurred")
    type: Optional[str] = Field(
        None, description="Type of internal transaction (e.g., 'CALL')")
    from_address: Optional[str] = Field(
        None, description="Sender address", alias="from")
    to: Optional[str] = Field(None, description="Recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    gas: Optional[str] = Field(None, description="Gas limit")
    gas_used: Optional[str] = Field(None, description="Gas used")
    input: Optional[str] = Field(
        None, description="Input data for the transaction")
    output: Optional[str] = Field(
        None, description="Output data from the transaction")


class NFTTransfer(BaseModel):
    """Represents an NFT transfer within a blockchain transaction."""
    token_address: Optional[str] = Field(
        None, description="Address of the NFT contract")
    token_id: Optional[str] = Field(
        None, description="ID of the transferred NFT")
    from_address_entity: Optional[str] = Field(
        None, description="Entity name of the sender address")
    from_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the sender entity")
    from_address: Optional[str] = Field(None, description="Sender address")
    from_address_label: Optional[str] = Field(
        None, description="Label of the sender address")
    to_address_entity: Optional[str] = Field(
        None, description="Entity name of the recipient address")
    to_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the recipient entity")
    to_address: Optional[str] = Field(None, description="Recipient address")
    to_address_label: Optional[str] = Field(
        None, description="Label of the recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    amount: Optional[str] = Field(
        None, description="Amount of NFTs transferred")
    contract_type: Optional[str] = Field(
        None, description="Type of NFT contract (e.g., 'ERC721', 'ERC1155')")
    block_number: Optional[str] = Field(
        None, description="Block number where this transfer occurred")
    block_timestamp: Optional[str] = Field(
        None, description="Block timestamp in ISO format")
    block_hash: Optional[str] = Field(
        None, description="Block hash where this transfer occurred")
    transaction_hash: Optional[str] = Field(
        None, description="Transaction hash of the transfer")
    transaction_type: Optional[str] = Field(
        None, description="Type of transaction")
    transaction_index: Optional[int] = Field(
        None, description="Index of the transaction in the block")
    log_index: Optional[int] = Field(
        None, description="Index of the log entry in the transaction receipt")
    operator: Optional[str] = Field(
        None, description="Address of the operator (for ERC1155 transfers)")
    possible_spam: Optional[str] = Field(
        None, description="Indicator if the NFT might be spam")
    verified_collection: Optional[str] = Field(
        None, description="Indicator if the collection is verified")


class ERC20Transfer(BaseModel):
    """Represents an ERC20 token transfer within a blockchain transaction."""
    token_name: Optional[str] = Field(
        None, description="Name of the transferred token")
    token_symbol: Optional[str] = Field(
        None, description="Symbol of the transferred token")
    token_logo: Optional[str] = Field(
        None, description="Logo URL of the token")
    token_decimals: Optional[str] = Field(
        None, description="Decimal places of the token")
    transaction_hash: Optional[str] = Field(
        None, description="Transaction hash of the transfer")
    address: Optional[str] = Field(
        None, description="Contract address of the token")
    block_timestamp: Optional[str] = Field(
        None, description="Block timestamp in ISO format")
    block_number: Optional[str] = Field(
        None, description="Block number where this transfer occurred")
    block_hash: Optional[str] = Field(
        None, description="Block hash where this transfer occurred")
    to_address_entity: Optional[str] = Field(
        None, description="Entity name of the recipient address")
    to_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the recipient entity")
    to_address: Optional[str] = Field(None, description="Recipient address")
    to_address_label: Optional[str] = Field(
        None, description="Label of the recipient address")
    from_address_entity: Optional[str] = Field(
        None, description="Entity name of the sender address")
    from_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the sender entity")
    from_address: Optional[str] = Field(None, description="Sender address")
    from_address_label: Optional[str] = Field(
        None, description="Label of the sender address")
    value: Optional[str] = Field(
        None, description="Value transferred in token's smallest unit")
    transaction_index: Optional[int] = Field(
        None, description="Index of the transaction in the block")
    log_index: Optional[int] = Field(
        None, description="Index of the log entry in the transaction receipt")
    possible_spam: Optional[str] = Field(
        None, description="Indicator if the token might be spam")
    verified_contract: Optional[str] = Field(
        None, description="Indicator if the contract is verified")


class NativeTransfer(BaseModel):
    """Represents a native token transfer (e.g., ETH) within a blockchain transaction."""
    from_address_entity: Optional[str] = Field(
        None, description="Entity name of the sender address")
    from_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the sender entity")
    from_address: Optional[str] = Field(None, description="Sender address")
    from_address_label: Optional[str] = Field(
        None, description="Label of the sender address")
    to_address_entity: Optional[str] = Field(
        None, description="Entity name of the recipient address")
    to_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the recipient entity")
    to_address: Optional[str] = Field(None, description="Recipient address")
    to_address_label: Optional[str] = Field(
        None, description="Label of the recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    value_formatted: Optional[str] = Field(
        None, description="Value formatted in the native token unit (e.g., ETH)")
    direction: Optional[str] = Field(
        None, description="Direction of transfer relative to the queried address (e.g., 'incoming', 'outgoing')")
    internal_transaction: Optional[bool] = Field(
        None, description="Indicator if this is an internal transaction")
    token_symbol: Optional[str] = Field(
        None, description="Symbol of the native token (e.g., 'ETH')")
    token_logo: Optional[str] = Field(
        None, description="Logo URL of the native token")


class WalletHistoryItem(BaseModel):
    """Represents a transaction in a wallet's history with detailed information."""
    hash: Optional[str] = Field(None, description="Transaction hash")
    nonce: Optional[str] = Field(None, description="Transaction nonce")
    transaction_index: Optional[str] = Field(
        None, description="Index of the transaction in the block")
    from_address_entity: Optional[str] = Field(
        None, description="Entity name of the sender address")
    from_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the sender entity")
    from_address: Optional[str] = Field(None, description="Sender address")
    from_address_label: Optional[str] = Field(
        None, description="Label of the sender address")
    to_address_entity: Optional[str] = Field(
        None, description="Entity name of the recipient address")
    to_address_entity_logo: Optional[str] = Field(
        None, description="Logo URL of the recipient entity")
    to_address: Optional[str] = Field(None, description="Recipient address")
    to_address_label: Optional[str] = Field(
        None, description="Label of the recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    gas: Optional[str] = Field(
        None, description="Gas limit set for the transaction")
    gas_price: Optional[str] = Field(None, description="Gas price in wei")
    receipt_cumulative_gas_used: Optional[str] = Field(
        None, description="Cumulative gas used in the block after this transaction")
    receipt_gas_used: Optional[str] = Field(
        None, description="Gas used by this transaction")
    receipt_contract_address: Optional[str] = Field(
        None, description="Contract address created, if the transaction was a contract creation")
    receipt_root: Optional[str] = Field(
        None, description="Transaction receipt root")
    receipt_status: Optional[str] = Field(
        None, description="Transaction receipt status (1 for success, 0 for failure)")
    block_timestamp: Optional[str] = Field(
        None, description="Block timestamp in ISO format")
    block_number: Optional[str] = Field(
        None, description="Block number where this transaction was included")
    block_hash: Optional[str] = Field(
        None, description="Block hash where this transaction was included")
    internal_transactions: Optional[List[InternalTransaction]] = Field(
        None, description="List of internal transactions")
    nft_transfers: Optional[List[NFTTransfer]] = Field(
        None, description="List of NFT transfers in this transaction")
    erc20_transfer: Optional[List[ERC20Transfer]] = Field(
        None, description="List of ERC20 token transfers in this transaction")
    native_transfers: Optional[List[NativeTransfer]] = Field(
        None, description="List of native token transfers in this transaction")


class WalletHistoryResponse(BaseModel):
    """Response model for wallet transaction history endpoint."""
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(
        None, description="Number of results per page")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    result: List[WalletHistoryItem] = Field(
        default_factory=list, description="List of transaction history items")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class WalletStatsInput(BaseModel):
    """Input model for get_wallet_stats function.
    Get the stats for a wallet address, including NFT counts, transaction counts, and transfer counts.
    """
    wallet_address: str = Field(..., description="Wallet address to get stats for")
    chain: Literal[
        "eth", "0x1",           # Ethereum
        "polygon", "0x89",      # Polygon
        "bsc", "0x38",          # Binance Smart Chain
        "avalanche", "0xa86a",  # Avalanche
        "fantom", "0xfa",       # Fantom
        "palm", "0x2a15c308d",  # Palm
        "cronos", "0x19",       # Cronos
        "arbitrum", "0xa4b1",   # Arbitrum
        "chiliz", "0x15b38",    # Chiliz
        "gnosis", "0x64",       # Gnosis
        "base", "0x2105",       # Base
        "optimism", "0xa",      # Optimism
        "linea", "0xe708",      # Linea
        "moonbeam", "0x504",    # Moonbeam
        "moonriver", "0x505",   # Moonriver
        "flow", "0x2eb",        # Flow
        "ronin", "0x7e4",       # Ronin
        "lisk", "0x46f",        # Lisk
        "pulse", "0x171"        # Pulse
    ] = Field("eth", description="The blockchain to query. Can be specified by chain name or chain ID.")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TransactionStats(BaseModel):
    """Statistics about transactions for a wallet."""
    total: Optional[str] = Field(None, description="Total number of transactions")


class TransferStats(BaseModel):
    """Statistics about transfers for a wallet."""
    total: Optional[str] = Field(None, description="Total number of transfers")


class WalletStatsResponse(BaseModel):
    """Response model for wallet stats endpoint."""
    nfts: Optional[str] = Field(None, description="Number of NFTs owned by the wallet")
    collections: Optional[str] = Field(None, description="Number of NFT collections owned by the wallet")
    transactions: Optional[TransactionStats] = Field(None, description="Transaction statistics")
    nft_transfers: Optional[TransferStats] = Field(None, description="NFT transfer statistics")
    token_transfers: Optional[TransferStats] = Field(None, description="Token transfer statistics")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TransactionDetailInput(BaseModel):
    """Input model for get_transaction_detail function.
    Get the contents of a transaction by the given transaction hash.
    """
    transaction_hash: str = Field(..., description="Transaction hash to be decoded")
    chain: Literal[
        "eth", "0x1",           # Ethereum
        "polygon", "0x89",      # Polygon
        "bsc", "0x38",          # Binance Smart Chain
        "avalanche", "0xa86a",  # Avalanche
        "fantom", "0xfa",       # Fantom
        "palm", "0x2a15c308d",  # Palm
        "cronos", "0x19",       # Cronos
        "arbitrum", "0xa4b1",   # Arbitrum
        "chiliz", "0x15b38",    # Chiliz
        "gnosis", "0x64",       # Gnosis
        "base", "0x2105",       # Base
        "optimism", "0xa",      # Optimism
        "linea", "0xe708",      # Linea
        "moonbeam", "0x504",    # Moonbeam
        "moonriver", "0x505",   # Moonriver
        "flow", "0x2eb",        # Flow
        "ronin", "0x7e4",       # Ronin
        "lisk", "0x46f",        # Lisk
        "pulse", "0x171"        # Pulse
    ] = Field("eth", description="The blockchain to query. Can be specified by chain name or chain ID.")
    include: Optional[str] = Field(None, description="Fields to include in the response")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TransactionDetailResponse(BaseModel):
    """Response model for transaction detail endpoint."""
    hash: Optional[str] = Field(None, description="Transaction hash")
    from_address_entity: Optional[str] = Field(None, description="Entity name of the sender address")
    from_address_entity_logo: Optional[str] = Field(None, description="Logo URL of the sender entity")
    from_address: Optional[str] = Field(None, description="Sender address")
    from_address_label: Optional[str] = Field(None, description="Label of the sender address")
    to_address_entity: Optional[str] = Field(None, description="Entity name of the recipient address")
    to_address_entity_logo: Optional[str] = Field(None, description="Logo URL of the recipient entity")
    to_address: Optional[str] = Field(None, description="Recipient address")
    to_address_label: Optional[str] = Field(None, description="Label of the recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    receipt_gas_used: Optional[str] = Field(None, description="Gas used by this transaction")
    receipt_contract_address: Optional[str] = Field(None, description="Contract address created, if the transaction was a contract creation")
    receipt_root: Optional[str] = Field(None, description="Transaction receipt root")
    receipt_status: Optional[str] = Field(None, description="Transaction receipt status (1 for success, 0 for failure)")
    block_timestamp: Optional[str] = Field(None, description="Block timestamp in ISO format")
    block_number: Optional[str] = Field(None, description="Block number where this transaction was included")
    block_hash: Optional[str] = Field(None, description="Block hash where this transaction was included")
    decoded_call: Optional[Dict[str, Any]] = Field(None, description="Decoded function call data if available")
    decoded_event: Optional[Dict[str, Any]] = Field(None, description="Decoded event data if available")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TokenInfo(BaseModel):
    """Information about a token in a token approval."""
    address: Optional[str] = Field(None, description="Token contract address")
    address_label: Optional[str] = Field(None, description="Label for the token address if available")
    name: Optional[str] = Field(None, description="Token name")
    symbol: Optional[str] = Field(None, description="Token symbol")
    logo: Optional[str] = Field(None, description="URL to token logo")
    possible_spam: Optional[str] = Field(None, description="Indicator if the token might be spam")
    verified_contract: Optional[str] = Field(None, description="Indicator if the contract is verified")
    current_balance: Optional[str] = Field(None, description="Current token balance in wei")
    current_balance_formatted: Optional[str] = Field(None, description="Current token balance formatted with decimals")
    usd_price: Optional[str] = Field(None, description="USD price of the token")
    usd_at_risk: Optional[str] = Field(None, description="USD value at risk due to this approval")


class SpenderInfo(BaseModel):
    """Information about a spender in a token approval."""
    address: Optional[str] = Field(None, description="Spender address")
    address_label: Optional[str] = Field(None, description="Label for the spender address if available")
    entity: Optional[str] = Field(None, description="Entity name of the spender")
    entity_logo: Optional[str] = Field(None, description="URL to entity logo")


class TokenApprovalItem(BaseModel):
    """Represents a token approval item."""
    block_number: Optional[str] = Field(None, description="Block number of the approval transaction")
    block_timestamp: Optional[str] = Field(None, description="Timestamp of the block in ISO format")
    transaction_hash: Optional[str] = Field(None, description="Transaction hash of the approval")
    value: Optional[str] = Field(None, description="Approved value in wei")
    value_formatted: Optional[str] = Field(None, description="Approved value formatted with decimals")
    token: Optional[TokenInfo] = Field(None, description="Information about the approved token")
    spender: Optional[SpenderInfo] = Field(None, description="Information about the spender")


class TokenApprovalInput(BaseModel):
    """Input model for get_token_approvals function.
    Get ERC20 approvals for a wallet address, ordered by block number in descending order.
    """
    wallet_address: str = Field(..., description="Wallet address to get token approvals for")
    chain: Literal[
        "eth", "0x1",           # Ethereum
        "polygon", "0x89",      # Polygon
        "bsc", "0x38",          # Binance Smart Chain
        "avalanche", "0xa86a",  # Avalanche
        "fantom", "0xfa",       # Fantom
        "palm", "0x2a15c308d",  # Palm
        "cronos", "0x19",       # Cronos
        "arbitrum", "0xa4b1",   # Arbitrum
        "chiliz", "0x15b38",    # Chiliz
        "gnosis", "0x64",       # Gnosis
        "base", "0x2105",       # Base
        "optimism", "0xa",      # Optimism
        "linea", "0xe708",      # Linea
        "moonbeam", "0x504",    # Moonbeam
        "moonriver", "0x505",   # Moonriver
        "flow", "0x2eb",        # Flow
        "ronin", "0x7e4",       # Ronin
        "lisk", "0x46f",        # Lisk
        "pulse", "0x171"        # Pulse
    ] = Field("eth", description="The blockchain to query. Can be specified by chain name or chain ID.")
    cursor: Optional[str] = Field(None, description="The cursor returned in the previous response (used for getting the next page)")
    limit: Optional[int] = Field(None, description="The number of token approvals to return (max 100)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TokenApprovalResponse(BaseModel):
    """Response model for token approvals endpoint."""
    page: Optional[int] = Field(None, description="Current page number")
    page_size: Optional[int] = Field(None, description="Number of results per page")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    result: List[TokenApprovalItem] = Field(default_factory=list, description="List of token approval items")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()

