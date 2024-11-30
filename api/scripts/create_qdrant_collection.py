import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from dotenv import load_dotenv

load_dotenv()


qdrant_url = os.environ.get("QDRANT_URL")
qdrant_collection = os.environ.get("QDRANT_COLLECTION")

qdrant = QdrantClient(url=qdrant_url)
qdrant.create_collection(
    collection_name=qdrant_collection,
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
    ),
)
