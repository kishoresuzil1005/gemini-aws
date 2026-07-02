from typing import List, Dict

from app.services.ai.embedding_service import EmbeddingService
from app.services.ai.qdrant_service import QdrantService


class DocumentRetriever:

    def __init__(self):

        self.embedding = EmbeddingService()
        self.qdrant = QdrantService()

    def search(
        self,
        question: str,
        limit: int = 5
    ) -> List[Dict]:

        try:

            vector = self.embedding.embed(question)

            results = self.qdrant.search(
                vector=vector,
                limit=limit
            )

            documents = []

            for result in results:

                # -----------------------------
                # Handle dictionary results
                # -----------------------------
                if isinstance(result, dict):

                    payload = result.get("payload", {})

                    documents.append(
                        {
                            "score": result.get("score", 0),
                            "title": payload.get("title"),
                            "source": payload.get("source"),
                            "content": payload.get("text"),
                        }
                    )

                # -----------------------------
                # Handle native Qdrant objects
                # -----------------------------
                else:

                    payload = result.payload

                    documents.append(
                        {
                            "score": result.score,
                            "title": payload.get("title"),
                            "source": payload.get("source"),
                            "content": payload.get("text"),
                        }
                    )

            return documents

        except Exception as e:

            print(f"[DocumentRetriever] search failed: {e}")
            return []


    def search_by_category(
        self,
        question: str,
        category: str,
        limit: int = 5
    ):

        try:
            vector = self.embedding.embed(question)
            return self.qdrant.search(
                vector=vector,
                limit=limit,
                filters={"category": category}
            )
        except Exception as e:
            print(f"[DocumentRetriever] search_by_category failed: {e}")
            return []

    def search_service_docs(
        self,
        service: str,
        limit: int = 10
    ):

        try:
            return self.qdrant.search_text(service, limit)
        except Exception as e:
            print(f"[DocumentRetriever] search_service_docs failed: {e}")
            return []

    def search_runbooks(
        self,
        issue: str,
        limit: int = 5
    ):

        try:
            return self.qdrant.search_text(f"runbook {issue}", limit)
        except Exception as e:
            print(f"[DocumentRetriever] search_runbooks failed: {e}")
            return []

    def search_best_practices(
        self,
        service: str
    ):

        try:
            return self.qdrant.search_text(f"{service} best practices", 5)
        except Exception as e:
            print(f"[DocumentRetriever] search_best_practices failed: {e}")
            return []
