import os
from typing import List, Dict, Any, Optional
from app.services.ai.embedding_service import EmbeddingService
from app.services.ai.qdrant_service import QdrantService
from app.services.ai.document_loader import DocumentLoader
from app.services.ai.ollama_service import OllamaService


class RAGService:
    def __init__(self, collection_name: str = "cloud_docs"):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService(collection_name=collection_name)
        self.document_loader = DocumentLoader()
        self.ollama_service = OllamaService()

    def index_document(self, title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Loads, splits, embeds, and upserts a document.
        """
        try:
            extra_meta = metadata or {}
            extra_meta["title"] = title
            
            # Split document into chunks
            chunks = self.document_loader.split_text(content, source=title, extra_metadata=extra_meta)
            if not chunks:
                return {"success": False, "message": "Document empty or no chunks created", "chunks_count": 0}

            # Generate embeddings and build payload
            points = []
            for chunk in chunks:
                vec = self.embedding_service.get_embedding(chunk["content"])
                points.append({
                    "id": chunk["id"],
                    "vector": vec,
                    "payload": {
                        "content": chunk["content"],
                        "metadata": chunk["metadata"]
                    }
                })

            # Upsert into Qdrant
            self.qdrant_service.upsert_vectors(points)
            return {
                "success": True,
                "document_id": title,
                "chunks_count": len(chunks)
            }
        except Exception as e:
            print(f"[RAG INDEX ERROR] Failed to index document: {e}")
            return {"success": False, "message": str(e), "chunks_count": 0}

    def index_directory(self, dir_path: str) -> int:
        """
        Helper to scan and ingest a local folder.
        """
        try:
            chunks = self.document_loader.load_and_split_directory(dir_path)
            if not chunks:
                return 0
            
            points = []
            for chunk in chunks:
                vec = self.embedding_service.get_embedding(chunk["content"])
                points.append({
                    "id": chunk["id"],
                    "vector": vec,
                    "payload": {
                        "content": chunk["content"],
                        "metadata": chunk["metadata"]
                    }
                })
                
            self.qdrant_service.upsert_vectors(points)
            return len(chunks)
        except Exception as e:
            print(f"[RAG INDEX DIRECTORY ERROR] {e}")
            return 0

    def query_rag(self, query: str, limit: int = 2) -> Dict[str, Any]:
        """
        Retrieves matching chunks and runs Ollama with the augmented context.
        """
        try:
            # Generate search query embedding
            query_vector = self.embedding_service.get_embedding(query)
            
            # Retrieve nearest neighbors
            matches = self.qdrant_service.search_similar(query_vector, limit=limit)
            
            # Build Context
            context_blocks = []
            references = []
            for idx, match in enumerate(matches):
                payload = match.get("payload", {})
                content = payload.get("content", "")
                meta = payload.get("metadata", {})
                source = meta.get("source", "Unknown Unit")
                
                context_blocks.append(f"Context [{idx+1}] (Source: {source}):\n{content}")
                references.append({
                    "source": source,
                    "score": match.get("score", 0.0),
                    "content": content,
                    "id": match.get("id")
                })
            
            context_str = "\n\n".join(context_blocks)
            
            # Construct Prompt
            augmented_prompt = (
                "You are an expert Cloud Operations and AWS Systems Architecture Assistant.\n"
                "Use the following pieces of context to answer the user's question. If you do not know the answer, "
                "say that you do not know or lack the information from the contexts - do not make up arbitrary information.\n\n"
                "=== RETRIEVED INFRASTRUCTURE CONTEXT ===\n"
                f"{context_str}\n"
                "========================================\n\n"
                f"User Question: {query}\n\n"
                "Formulate a precise, operational, professional, and clear answer:"
            )
            
            # Request completion from Ollama
            answer = self.ollama_service.generate(augmented_prompt)
            
            return {
                "answer": answer,
                "sources": references,
                "prompt_rendered": augmented_prompt
            }
        except Exception as e:
            print(f"[RAG QUERY ERROR] {e}")
            return {
                "answer": f"I encountered an error retrieving or constructing the answer. Please verify connections. Details: {e}",
                "sources": [],
                "prompt_rendered": ""
            }
