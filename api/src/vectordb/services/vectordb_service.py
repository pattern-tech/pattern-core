import os
from typing import Any, List

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import Qdrant

from dotenv import load_dotenv

load_dotenv()


class VectorDBService:
    def __init__(self):
        self.qdrant_url = os.environ.get("QDRANT_URL")
        self.qdrant_collection = os.environ.get("QDRANT_COLLECTION")

        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Qdrant.from_existing_collection(
            embedding=self.embeddings,
            collection_name=self.qdrant_collection,
            url=self.qdrant_url,
        )

    def add_documents(self, documents: List[Document], ids: List[str]):
        """
        Args:
            documents:
                [Document(
                    page_content="sample text",
                    metadata={"source": "xyz"},
                )]
        """
        self.vector_store.add_documents(documents=documents, ids=ids)

    def similarity_search(self, query: str, k: int = 1, filter: Any = None):
        """
        Args:
            filter(obj): {"KEY": "VALUE"}
        """
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
        )
