from typing import List, Dict

from app.ai.services.embedding_service import EmbeddingService
from app.ai.services.qdrant_service import QdrantService


class DocumentRetriever:

    def __init__(self):

        self.embedding = EmbeddingService()
        self.qdrant = QdrantService()

    def search(
        self,
        question: str,
        limit: int = 5
    ) -> List[Dict]:

        vector = self.embedding.embed(question)

        results = self.qdrant.search(
            vector=vector,
            limit=limit
        )

        documents = []

        for result in results:

            payload = result.payload

            documents.append(
                {
                    "score": result.score,
                    "title": payload.get("title"),
                    "source": payload.get("source"),
                    "content": payload.get("text")
                }
            )

        return documents

    def search_by_category(
        self,
        question: str,
        category: str,
        limit: int = 5
    ):

        vector = self.embedding.embed(question)

        return self.qdrant.search(
            vector=vector,
            limit=limit,
            filters={
                "category": category
            }
        )

    def search_service_docs(
        self,
        service: str,
        limit: int = 10
    ):

        return self.qdrant.search_text(
            service,
            limit
        )

    def search_runbooks(
        self,
        issue: str,
        limit: int = 5
    ):

        return self.qdrant.search_text(
            f"runbook {issue}",
            limit
        )

    def search_best_practices(
        self,
        service: str
    ):

        return self.qdrant.search_text(
            f"{service} best practices",
            5
        )
