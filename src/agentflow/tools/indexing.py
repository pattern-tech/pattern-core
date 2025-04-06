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
    input_schema: Optional[Dict] = None
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
