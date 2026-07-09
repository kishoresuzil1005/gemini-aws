import time
from app.services.ai.assistant.tool_registry import BaseTool
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.ai.embedding_service import EmbeddingService
from app.services.ai.qdrant_service import QdrantService

class DocumentationTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.embedding = EmbeddingService()
        self.qdrant = QdrantService("cloud_docs")

    @property
    def name(self) -> str:
        return "DOCUMENTATION"

    def execute(self, resource_id: str, **kwargs) -> ToolResponse:
        start_time = time.time()
        
        query = kwargs.get("query") or resource_id or "AWS Documentation"
        
        # 1. & 2. Get top chunks
        query_vector = self.embedding.get_embedding(query)
        raw_results = self.qdrant.search_similar(query_vector, limit=3)
        
        filtered_results = [r for r in raw_results if r.get("score", 0) > 0.80]
        
        # 3. & 5. Build structured context and sources
        formatted_docs = []
        sources = []
        
        for i, doc in enumerate(filtered_results, start=1):
            title = doc.get('title') or doc.get('source') or f"Document {i}"
            content = doc.get('content', '')
            formatted_docs.append(f"Document {i}\n{title}\n{content}")
            
            sources.append({
                "document": title,
                "score": doc.get('score', 0)
            })
            
        if not formatted_docs:
            context = "No highly relevant documentation found for the query."
        else:
            context = "Relevant Documentation\n\n" + "\n\n".join(formatted_docs)
            
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Embed sources into context so context_builder picks it up, or return as metadata
        return ToolResponse(
            tool_name=self.name,
            status="SUCCESS",
            execution_time_ms=execution_time_ms,
            context={"results": context, "sources": sources}
        )
