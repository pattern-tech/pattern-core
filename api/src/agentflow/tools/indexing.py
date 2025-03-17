import numpy as np
from qdrant_client.http import models
from qdrant_client import QdrantClient
from typing import List, Dict, Any, Optional
import os
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from openai import OpenAI
from qdrant_client.http.models.models import ScoredPoint


class FunctionSchema(BaseModel):
    """Schema for storing function information."""
    function_name: str
    description: str
    output_schema: Optional[Dict] = None
    parameters: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    def to_dict(self):
        return self.model_dump()


class FunctionIndexer:
    def __init__(self, collection_name: str = "functions"):
        """Initialize the function indexer with Qdrant and OpenAI embedding model."""
        # Initialize Qdrant client
        self.qdrant_url = os.environ.get("QDRANT_URL", "localhost")
        self.qdrant_port = int(os.environ.get("QDRANT_PORT", 6333))
        self.client = QdrantClient(url=self.qdrant_url, port=self.qdrant_port)

        # Initialize OpenAI client
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided or set as OPENAI_API_KEY environment variable")
        self.openai_client = OpenAI(api_key=self.api_key)

        # Set vector size for text-embedding-ada-002 model
        self.vector_size = 1536  # OpenAI's text-embedding-ada-002 dimension
        self.collection_name = collection_name

        # Create collection if it doesn't exist
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        """Create a Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE
                )
            )
            print(f"Collection '{self.collection_name}' created.")

    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text string using OpenAI's embedding model."""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    def index_function(self, function: FunctionSchema) -> str:
        """Index a function in the Qdrant database."""
        # Create embedding from function name and description
        text_to_embed = f"{function.function_name}: {function.description}"
        embedding = self._get_embedding(text_to_embed)

        # Create payload
        payload = function.to_dict()

        # Add to Qdrant
        # Convert function name to a positive integer ID using a more reliable method
        # We use abs() to ensure it's positive and then modulo to keep it within uint64 range
        function_id = abs(hash(function.function_name)) % (2**63 - 1)

        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=function_id,  # Use positive integer ID
                    vector=embedding,
                    payload=payload
                )
            ]
        )

        return f"Function '{function.function_name}' indexed successfully."

    def search_functions(self, query: str, limit: int = 10) -> List[ScoredPoint]:
        """Search for functions by query string."""
        query_embedding = self._get_embedding(query)

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit
        )

        return search_result

    def get_all_functions(self) -> List[ScoredPoint]:
        """Get all indexed functions."""
        result = self.client.scroll(
            collection_name=self.collection_name,
            limit=100,  # Adjust as needed
            with_payload=True,
            with_vectors=False
        )

        return result


if __name__ == "__main__":
    # Example usage
    # Make sure to set your OpenAI API key as an environment variable or pass it directly
    # export OPENAI_API_KEY="your-api-key"
    indexer = FunctionIndexer(
        api_key="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")
    # functions = []

    # function = FunctionSchema(
    #     name="get_current_timestamp",
    #     description="Get the current Unix timestamp",
    #     # parameters={
    #     #     "id": {
    #     #         "type": "string",
    #     #         "description": "User ID"
    #     #     }
    #     # },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="convert_to_timestamp",
    #     description="Convert a natural language date string into a Unix timestamp.",
    #     parameters={
    #         "date_str": {
    #             "type": "string",
    #             "description": "A human-readable date (e.g., 'one month ago', '12/3/2020')"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_contract_source_code",
    #     description="Retrieve the source code of a smart contract",
    #     parameters={
    #         "contract_address": {
    #             "type": "string",
    #             "description": "The contract address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_contract_abi",
    #     description="Retrieve the ABI of a smart contract",
    #     parameters={
    #         "contract_address": {
    #             "type": "string",
    #             "description": "The contract address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_abi_of_event",
    #     description="Retrieve the ABI of a specific event from a smart contract.",
    #     parameters={
    #         "contract_address": {
    #             "type": "string",
    #             "description": "The smart contract address"
    #         },
    #         "event_name": {
    #             "type": "string",
    #             "description": "The name of the event"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_contract_events",
    #     description="Fetch events for a given smart contract event within a block range.",
    #     parameters={
    #         "contract_address": {
    #             "type": "string",
    #             "description": "The smart contract address"
    #         },
    #         "event_name": {
    #             "type": "string",
    #             "description": "The name of the event"
    #         },
    #         "from_block": {
    #             "type": "integer",
    #             "description": "The starting block (default: current block - 10)"
    #         },
    #         "to_block": {
    #             "type": "integer",
    #             "description": "The ending block (default: current block)"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_latest_eth_block_number",
    #     description="Retrieve the latest Ethereum block number.",
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="convert_timestamp_to_block_number",
    #     description="Convert a Unix timestamp to the nearest Ethereum block number",
    #     parameters={
    #         "timestamp": {
    #             "type": "int",
    #             "description": "The Unix timestamp"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="convert_timestamp_to_block_number",
    #     description="Convert a Unix timestamp to the nearest Ethereum block number",
    #     parameters={
    #         "timestamp": {
    #             "type": "int",
    #             "description": "The Unix timestamp"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_wallet_active_chains",
    #     description="Get active chains for a wallet address across all chains",
    #     parameters={
    #         "timestamp": {
    #             "type": "string",
    #             "description": "Ethereum wallet address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_wallet_token_balances",
    #     description="Get token balances for a specific wallet address and their token prices in USD. (paginated)",
    #     parameters={
    #         "wallet_address": {
    #             "type": "string",
    #             "description": "Ethereum wallet address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_wallet_stats",
    #     description="Get the stats for a wallet address",
    #     parameters={
    #         "wallet_address": {
    #             "type": "string",
    #             "description": "Ethereum wallet address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_wallet_history",
    #     description="Retrieve the full transaction history of a specified wallet address, including sends, receives, token and NFT transfers and contract interactions. (paginated & in descending order)",
    #     parameters={
    #         "wallet_address": {
    #             "type": "string",
    #             "description": "Ethereum wallet address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_transaction_detail",
    #     description="Get the contents of a transaction by the given transaction hash",
    #     parameters={
    #         "transaction_hash": {
    #             "type": "string",
    #             "description": "transaction hash to be decoded"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # function = FunctionSchema(
    #     name="get_token_approvals",
    #     description="Get ERC20 approvals for one or many wallet addresses and/or contract addresses, ordered by block number in descending order",
    #     parameters={
    #         "wallet_address": {
    #             "type": "string",
    #             "description": "Ethereum wallet address"
    #         }
    #     },
    #     tags=["blockchain"]
    # )
    # functions.append(function)

    # for function in functions:
    #     indexer.index_function(function)

    indexer.search_functions(
        "Which functions should i call to transfer USDC with the following contract? [0x43506849d7c04f9138d1a2050bbf3a0c054402dd]")
    # print(indexer.get_all_functions())
