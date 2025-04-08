from pydantic import BaseModel, Field
from typing import List, Any, Optional, Dict, Literal


class ContractAbiInput(BaseModel):
    """Input model for fetch_contract_abi and get_contract_abi functions.
    Retrieve the ABI of a smart contract from the blockchain explorer API.
    """
    contract_address: str = Field(..., description="The contract address")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractSourceCodeInput(BaseModel):
    """Input model for fetch_contract_source_code and get_contract_source_code functions.
    Retrieve the source code of a smart contract from the blockchain explorer API.
    """
    contract_address: str = Field(..., description="The contract address")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class EventAbiInput(BaseModel):
    """Input model for get_event_abi function.
    Retrieve the ABI entry for a specific event.
    """
    abi: List[Dict] = Field(..., description="The list of ABI definitions")
    event_name: str = Field(..., description="The name of the event")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TimestampToBlockNumberInput(BaseModel):
    """Input model for timestamp_to_block_number and convert_timestamp_to_block_number functions.
    Convert a given Unix timestamp to the nearest blockchain block number.
    """
    timestamp: int = Field(..., description="Unix timestamp")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ConvertToTimestampInput(BaseModel):
    """Input model for convert_to_timestamp function.
    Convert a natural language date string into a Unix timestamp.
    """
    date_str: str = Field(
        ..., description="A human-readable date (e.g., \"one month ago\", \"12/3/2020\")")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class EventAbiOfContractInput(BaseModel):
    """Input model for get_abi_of_event function.
    Retrieve the ABI of a specific event from a smart contract.
    """
    contract_address: str = Field(...,
                                  description="The smart contract address")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")
    event_name: str = Field(...,
                            description="The name of the event to retrieve the ABI for")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractEventsInput(BaseModel):
    """Input model for get_contract_events function.
    Fetch events for a given smart contract event within a block range.
    """
    contract_address: str = Field(...,
                                  description="The smart contract address")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")
    event_name: str = Field(...,
                            description="The name of the event to retrieve")
    from_block: Optional[int] = Field(
        None, description="The starting block number to fetch events from")
    to_block: Optional[int] = Field(
        None, description="The ending block number to fetch events to")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class LatestBlockNumberInput(BaseModel):
    """Input model for get_latest_chain_block_number function.
    Retrieve the latest chain block number.
    """
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class LatestBlockHashInput(BaseModel):
    """Input model for get_latest_eth_block_hash function.
    Retrieve the hash of the latest chain block.
    """
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class BlockTransactionsInput(BaseModel):
    """Input model for get_block_transactions function.
    Retrieve all transactions in a specific blockchain block.
    """
    block_number: int = Field(...,
                              description="The block number to retrieve transactions from")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")
    output_include: List[str] = Field(
        ..., description="List of transaction fields to include in the output")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractFunctionCallInput(BaseModel):
    """Input model for call_contract_function function.
    Call a read-only function on a smart contract and return the result.
    """
    contract_address: str = Field(...,
                                  description="The smart contract address")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")
    function_name: str = Field(...,
                               description="The name of the function to call")
    function_params: Optional[List[Any]] = Field(
        None, description="The parameters to pass to the function")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


# Pydantic models for responses

# Common components for responses
class EventParameter(BaseModel):
    """Represents a parameter in a contract event."""
    name: Optional[str] = Field(None, description="Name of the parameter")
    type: Optional[str] = Field(
        None, description="Type of the parameter (e.g., 'address', 'uint256')")
    indexed: Optional[bool] = Field(
        None, description="Whether the parameter is indexed")
    value: Optional[Any] = Field(None, description="Value of the parameter")


class ContractEvent(BaseModel):
    """Represents a contract event."""
    event_name: Optional[str] = Field(None, description="Name of the event")
    block_number: Optional[int] = Field(
        None, description="Block number where the event was emitted")
    block_timestamp: Optional[str] = Field(
        None, description="Timestamp of the block in ISO format")
    transaction_hash: Optional[str] = Field(
        None, description="Transaction hash that emitted the event")
    log_index: Optional[int] = Field(
        None, description="Index of the log in the transaction receipt")
    address: Optional[str] = Field(
        None, description="Contract address that emitted the event")
    parameters: Optional[List[EventParameter]] = Field(
        None, description="Parameters of the event")


class BlockTransaction(BaseModel):
    """Represents a transaction in a block."""
    hash: Optional[str] = Field(None, description="Transaction hash")
    block_number: Optional[int] = Field(
        None, description="Block number containing the transaction")
    block_timestamp: Optional[str] = Field(
        None, description="Timestamp of the block in ISO format")
    from_address: Optional[str] = Field(None, description="Sender address")
    to_address: Optional[str] = Field(None, description="Recipient address")
    value: Optional[str] = Field(None, description="Value transferred in wei")
    gas: Optional[int] = Field(None, description="Gas limit")
    gas_price: Optional[str] = Field(None, description="Gas price in wei")
    input: Optional[str] = Field(
        None, description="Input data for the transaction")
    nonce: Optional[int] = Field(None, description="Transaction nonce")
    transaction_index: Optional[int] = Field(
        None, description="Index of the transaction in the block")


class ContractAbiItem(BaseModel):
    """Represents an item in a contract ABI."""
    type: Optional[str] = Field(
        None, description="Type of the ABI item (e.g., 'function', 'event')")
    name: Optional[str] = Field(
        None, description="Name of the function or event")
    inputs: Optional[List[Dict[str, Any]]] = Field(
        None, description="Input parameters")
    outputs: Optional[List[Dict[str, Any]]] = Field(
        None, description="Output parameters for functions")
    stateMutability: Optional[str] = Field(
        None, description="State mutability for functions (e.g., 'view', 'pure')")
    constant: Optional[bool] = Field(
        None, description="Whether the function is constant")
    payable: Optional[bool] = Field(
        None, description="Whether the function is payable")
    anonymous: Optional[bool] = Field(
        None, description="Whether the event is anonymous (for events)")


class ContractAbiResponse(BaseModel):
    """Response model for contract ABI endpoints.
    Contains the contract ABI as a list of ABI items.
    """
    items: List[ContractAbiItem] = Field(
        default_factory=list, description="List of ABI items")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractSourceCodeResponse(BaseModel):
    """Response model for contract source code endpoints.
    Contains the contract source code and related information.
    """
    """Represents the source code of a contract."""
    SourceCode: Optional[str] = Field(
        None, description="Source code of the contract")
    ABI: Optional[str] = Field(
        None, description="ABI of the contract as a JSON string")
    ContractName: Optional[str] = Field(
        None, description="Name of the contract")
    CompilerVersion: Optional[str] = Field(
        None, description="Compiler version used")
    OptimizationUsed: Optional[str] = Field(
        None, description="Whether optimization was used")
    Runs: Optional[str] = Field(
        None, description="Number of optimization runs")
    ConstructorArguments: Optional[str] = Field(
        None, description="Constructor arguments used for deployment")
    EVMVersion: Optional[str] = Field(None, description="EVM version targeted")
    Library: Optional[str] = Field(None, description="Libraries used")
    LicenseType: Optional[str] = Field(None, description="License type")
    Proxy: Literal["1", "0"] = Field(
        None, description="Whether this is a proxy contract")
    Implementation: Optional[str] = Field(
        None, description="Implementation address if this is a proxy",)
    SwarmSource: Optional[str] = Field(None, description="Swarm source")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class EventAbiResponse(BaseModel):
    """Response model for event ABI endpoints.
    Contains the ABI of a specific event.
    """
    event_name: Optional[str] = Field(None, description="Name of the event")
    inputs: Optional[List[Dict[str, Any]]] = Field(
        None, description="Input parameters of the event")
    anonymous: Optional[bool] = Field(
        None, description="Whether the event is anonymous")
    type: str = Field("event", description="Type of the ABI item")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class BlockNumberResponse(BaseModel):
    """Response model for block number endpoints.
    Contains a block number.
    """
    block_number: int = Field(..., description="Block number")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class TimestampResponse(BaseModel):
    """Response model for timestamp endpoints.
    Contains a Unix timestamp.
    """
    timestamp: int = Field(..., description="Unix timestamp")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractEventsResponse(BaseModel):
    """Response model for contract events endpoints.
    Contains a list of events emitted by the contract.
    """
    events: List[ContractEvent] = Field(
        default_factory=list, description="List of contract events")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class BlockHashResponse(BaseModel):
    """Response model for block hash endpoints.
    Contains a block hash.
    """
    block_hash: str = Field(..., description="Block hash")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class BlockTransactionsResponse(BaseModel):
    """Response model for block transactions endpoints.
    Contains a list of transactions in a block.
    """
    transactions: List[BlockTransaction] = Field(
        default_factory=list, description="List of transactions in the block")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class ContractFunctionCallResponse(BaseModel):
    """Response model for contract function call endpoint.
    Contains the function call result and metadata.
    """
    success: bool = Field(...,
                          description="Whether the function call was successful")
    result: Optional[Any] = Field(
        None, description="Result of the function call")
    error: Optional[str] = Field(
        None, description="Error message if the call failed")
    result_type: Optional[str] = Field(None, description="Type of the result")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class CurrentTimestampInput(BaseModel):
    """Input model for get_current_timestamp function.
    Get the current Unix timestamp.
    """

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class CurrentTimestampResponse(BaseModel):
    """Response model for get_current_timestamp endpoint.
    Contains the current Unix timestamp.
    """
    timestamp: int = Field(..., description="Current Unix timestamp")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class DecodeTransactionInput(BaseModel):
    """Input model for decode_transaction_input function.
    Decode the input data of an Ethereum transaction using the ABI of the contract.
    """
    transaction_input: str = Field(
        ..., description="The input data of the transaction (hex string starting with '0x')")
    contract_address: str = Field(
        ..., description="The address of the contract that was called in the transaction")
    chain_id: Literal["1", "42161", "8453", "137", "250"] = Field(
        ..., description="The chain ID: 1 (Ethereum), 42161 (Arbitrum), 8453 (Base), 137 (Polygon), 250 (Fantom)")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()


class DecodedParameter(BaseModel):
    """Represents a decoded parameter from a transaction input."""
    name: Optional[str] = Field(None, description="Name of the parameter")
    type: str = Field(...,
                      description="Type of the parameter (e.g., 'address', 'uint256')")
    value: Any = Field(..., description="Decoded value of the parameter")


class DecodeTransactionResponse(BaseModel):
    """Response model for decode_transaction_input endpoint.
    Contains the decoded transaction input with function name, signature, and parameters.
    """
    function_name: str = Field(...,
                               description="Name of the function that was called")
    function_signature: str = Field(
        ..., description="Signature of the function (e.g., 'transfer(address,uint256)')")
    parameters: List[DecodedParameter] = Field(
        default_factory=list, description="Decoded parameters of the function call")

    @classmethod
    def to_json_schema(cls) -> str:
        """Return the JSON Schema representation of the model as a JSON string."""
        return cls.model_json_schema()
