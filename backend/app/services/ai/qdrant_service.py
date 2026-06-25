import os
from typing import List, Dict, Any, Optional

class QdrantService:
    def __init__(self, collection_name: str = "cloud_docs"):
        self.collection_name = collection_name
        self.client = None
        self.dimension = 768
        self._local_storage = {}
        
        try:
            from qdrant_client import QdrantClient
            qdrant_host = os.getenv("QDRANT_HOST", "localhost")
            qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
            
            # First try connecting to real Qdrant server, fallback to memory
            try:
                self.client = QdrantClient(host=qdrant_host, port=qdrant_port, timeout=5)
                # Test connectivity
                self.client.get_collections()
                print(f"[QDRANT SERVICE] Connected successfully to {qdrant_host}:{qdrant_port}")
            except Exception:
                print("[QDRANT SERVICE] Real Qdrant server not reachable. Using in-memory Qdrant client.")
                self.client = QdrantClient(":memory:")
                
            self.create_collection_if_not_exists()
        except Exception as e:
            print(f"[QDRANT SERVICE WARNING] Qdrant client library error, using secondary internal storage fallback: {e}")
            self.client = None
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
                print(f"[QDRANT] Collection '{self.collection_name}' created successfully.")
        except Exception as e:
            print(f"[QDRANT ERROR] Failed to create collection: {e}")

    def upsert_vectors(self, points: List[Dict[str, Any]]):
        """
        points list: [{"id": int/str, "vector": list, "payload": dict}]
        """
        if self.client is not None:
            try:
                from qdrant_client.http.models import PointStruct
                qdrant_points = []
                for pt in points:
                    import uuid
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
                print(f"[QDRANT UPSERT ERROR] {e}. Falling back to local dictionary storage.")
        
        # Fallback dictionary storage
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
                print(f"[QDRANT SEARCH ERROR] {e}. Searching fallback dictionary.")

        # Fallback local search
        import numpy as np
        results = []
        qv = np.array(query_vector)
        qv_norm = np.linalg.norm(qv)

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
