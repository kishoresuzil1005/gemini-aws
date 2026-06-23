from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(
    host="localhost",
    port=6333
)

client.create_collection(
    collection_name="cloud_docs",
    vectors_config=VectorParams(
        size=768,
        distance=Distance.COSINE
    )
)

print("cloud_docs created")
