import os
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.environ.get("QDRANT_URL")
qdrant_collection = os.environ.get("QDRANT_COLLECTION")

qdrant = QdrantClient(url=qdrant_url)

# Retrieve all collections from Qdrant
collections_info = qdrant.get_collections()
existing_collections = [col.name for col in collections_info.collections]

# Check if the collection already exists
if qdrant_collection in existing_collections:
    print(f"Collection '{qdrant_collection}' already exists. Doing nothing.")
else:
    print(
        f"Collection '{qdrant_collection}' does not exist. Creating collection...")
    qdrant.create_collection(
        collection_name=qdrant_collection,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )
