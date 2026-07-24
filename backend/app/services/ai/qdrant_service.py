import os
import threading
import logging
import uuid
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self, collection_name: str = "cloud_docs", embedding_service=None):
        self.collection_name = collection_name
        self.client = None
        self.dimension = 768
        self._local_storage = {}
        self._local_storage_lock = threading.RLock()
        self.embedding_service = embedding_service
        
        try:
            from qdrant_client import QdrantClient
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
            
            # First try connecting to real Qdrant server, fallback to memory
            try:
                self.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=5)
                # Test connectivity
                self.client.get_collections()
                logger.info(f"Connected successfully to Qdrant at {qdrant_host}:{qdrant_port}")
            except Exception as e:
                logger.warning(f"Real Qdrant server not reachable. Using in-memory Qdrant client. Reason: {e}")
                self.client = QdrantClient(":memory:")
                
            self.create_collection_if_not_exists()
        except Exception as e:
            logger.error(f"Qdrant client library error, using secondary internal storage fallback: {e}")
            self.client = None
            with self._local_storage_lock:
                self._local_storage = {}

    def create_collection_if_not_exists(self):
        if self.client is None:
            return
        
        try:
            from qdrant_client.http.models import Distance, VectorParams
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
                )
                logger.info(f"Collection '{self.collection_name}' created successfully.")
        except Exception as e:
            logger.exception(f"Failed to create collection '{self.collection_name}': {e}")

    def upsert_vectors(self, points: List[Dict[str, Any]]) -> bool:
        """
        points list: [{"id": int/str, "vector": list, "payload": dict}]
        """
        if self.client is not None:
            try:
                from qdrant_client.http.models import PointStruct
                qdrant_points = []
                for pt in points:
                    pt_id = pt.get("id")
                    if isinstance(pt_id, str):
                        try:
                            # Qdrant requires UUID string or integer for point IDs
                            # convert custom UUID or generate deterministic UUID from string
                            pt_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, pt_id))
                        except Exception:
                            pt_id = str(uuid.uuid4())
                    
                    qdrant_points.append(PointStruct(
                        id=pt_id,
                        vector=pt["vector"],
                        payload=pt["payload"]
                    ))
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=qdrant_points
                )
                return True
            except Exception as e:
                logger.exception(f"Qdrant upsert error. Falling back to local dictionary storage: {e}")
        
        # Fallback dictionary storage
        with self._local_storage_lock:
            for pt in points:
                self._local_storage[str(pt.get("id"))] = {
                    "vector": pt["vector"],
                    "payload": pt["payload"]
                }
        return True

    def search_similar(self, query_vector: List[float], limit: int = 5, categories: List[str] = None) -> List[Dict[str, Any]]:
        if self.client is not None:
            try:
                from qdrant_client.http.models import Filter, FieldCondition, MatchAny
                
                query_filter = None
                if categories:
                    query_filter = Filter(
                        must=[
                            FieldCondition(
                                key="metadata.category",
                                match=MatchAny(any=categories)
                            )
                        ]
                    )
                    
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    query_filter=query_filter,
                    limit=limit
                )
                results = response.points
                return [
                    {
                        "id": point.id,
                        "score": point.score,
                        "payload": point.payload
                    }
                    for point in results
                ]
            except Exception as e:
                logger.exception(f"Qdrant search error. Searching fallback dictionary: {e}")

        # Fallback local search
        import numpy as np
        results = []
        qv = np.array(query_vector)
        qv_norm = np.linalg.norm(qv)

        with self._local_storage_lock:
            for k, item in self._local_storage.items():
                payload = item.get("payload", {})
                metadata = payload.get("metadata", {})
                item_category = metadata.get("category")
                
                # Filter by categories if provided
                if categories and item_category not in categories:
                    continue
                    
                v = np.array(item["vector"])
                v_norm = np.linalg.norm(v)
                if qv_norm > 0 and v_norm > 0:
                    score = float(np.dot(qv, v) / (qv_norm * v_norm))
                else:
                    score = 0.0
                results.append({
                    "id": k,
                    "score": score,
                    "payload": payload
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    # --------------------------------------------------
    # Compatibility wrapper
    # --------------------------------------------------

    def search(
        self,
        vector,
        limit: int = 5,
        filters: dict | None = None
    ):
        """
        Backward-compatible wrapper used by DocumentRetriever.
        """

        categories = None

        if filters:
            categories = filters.get("category")

            if categories and not isinstance(categories, list):
                categories = [categories]

        return self.search_similar(
            query_vector=vector,
            limit=limit,
            categories=categories
        )

    def search_text(self, text: str, limit: int = 5):
        """
        Placeholder until semantic text search is implemented.
        """
        # Inject embedding service if not provided to preserve backwards compatibility
        if not self.embedding_service:
            from app.services.ai.embedding_service import EmbeddingService
            self.embedding_service = EmbeddingService()

        embedding = self.embedding_service.embed(text)

        return self.search(
            vector=embedding,
            limit=limit
        )