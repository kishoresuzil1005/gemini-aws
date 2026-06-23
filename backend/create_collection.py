import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv

load_dotenv()

try:
    client = QdrantClient(
        host=os.getenv("QDRANT_HOST", "localhost"),
        port=int(os.getenv("QDRANT_PORT", 6333))
    )

    client.create_collection(
        collection_name="cloud_docs",
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE
        )
    )

    print("cloud_docs created")
except Exception as e:
    print(f"Warning: Could not connect to Qdrant to create collection: {e}. If Qdrant is not running, the application will use the in-memory fallback.")
