import os
from typing import List, Dict, Any, Optional
from app.services.ai.embedding_service import EmbeddingService
from app.services.ai.qdrant_service import QdrantService
from app.services.ai.document_loader import DocumentLoader
from app.services.ai.ollama_service import OllamaService
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.retrieval_optimizer import RetrievalOptimizer


class RAGService:
    def __init__(self, collection_name: str = "cloud_docs"):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService(collection_name=collection_name)
        self.document_loader = DocumentLoader()
        self.ollama_service = OllamaService()
        self.prompt_builder = PromptBuilder()
        self.retrieval_optimizer = RetrievalOptimizer(min_score=0.65)

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
            total = len(chunks)

            for i, chunk in enumerate(chunks, start=1):

                if i % 10 == 0:
                    print(f"[EMBEDDING] {i}/{total}")

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

    def query_rag(self, query: str, limit: int = 8) -> Dict[str, Any]:
        """
        Retrieves matching chunks, optimizes context with RetrievalOptimizer, 
        and runs Ollama with the structured context.
        """
        try:
            INITIAL_RETRIEVAL = 20
            FINAL_CONTEXT = limit
            
            # Generate search query embedding
            query_vector = self.embedding_service.get_embedding(query)
            
            # Retrieve nearest neighbors
            matches = self.qdrant_service.search_similar(query_vector, limit=INITIAL_RETRIEVAL)
            
            # Optimize Context
            optimization_result = self.retrieval_optimizer.optimize(query, matches, final_k=FINAL_CONTEXT)
            optimized_chunks = optimization_result["optimized_chunks"]
            retrieval_stats = optimization_result["stats"]
            
            num_chunks = len(optimized_chunks)
            
            # Skip LLM if no valid chunks remain
            if num_chunks == 0:
                return {
                    "answer": "The retrieved documentation does not contain enough information.",
                    "confidence": 0.0,
                    "retrieval": retrieval_stats,
                    "sources": [],
                    "hallucination_check": "BLOCKED"
                }
                
            # Build Structured Context
            context_blocks = []
            references = []
            total_score = 0.0
            
            for m in optimized_chunks:
                score = m.get("score", 0.0)
                payload = m.get("payload", {})
                content = payload.get("content", "").strip()
                meta = payload.get("metadata", {})
                source = meta.get("source", "Unknown Document")
                
                context_block = f"==========\nDocument\n{source}\n==========\n{content}\n"
                context_blocks.append(context_block)
                
                references.append({
                    "source": source,
                    "score": score,
                    "rerank_score": m.get("rerank_score", score),
                    "content": content,
                    "id": m.get("id")
                })
                total_score += score
                
            confidence = total_score / num_chunks
            context_str = "\n".join(context_blocks)
            
            # Construct Prompt
            augmented_prompt = self.prompt_builder.build(query=query, context=context_str)
            
            # Request completion from Ollama
            answer = self.ollama_service.generate(augmented_prompt)
            
            # Validate the Final Answer
            hallucination_indicators = [
                "Generally", "Typically", "Usually", "In most cases", 
                "Normally", "It depends"
            ]
            
            hallucination_status = "PASSED"
            answer_lower = answer.lower()
            for indicator in hallucination_indicators:
                if indicator.lower() in answer_lower:
                    hallucination_status = "WARNING_POSSIBLE_HALLUCINATION"
                    break
            
            return {
                "answer": answer,
                "confidence": confidence,
                "retrieval": retrieval_stats,
                "sources": references,
                "prompt_rendered": augmented_prompt,
                "hallucination_check": hallucination_status
            }
        except Exception as e:
            print(f"[RAG QUERY ERROR] {e}")
            return {
                "answer": f"I encountered an error retrieving or constructing the answer. Please verify connections. Details: {e}",
                "confidence": 0.0,
                "retrieval": {
                    "retrieved": 0, "filtered": 0, "duplicates_removed": 0, "reranked": 0, "used": 0
                },
                "sources": [],
                "prompt_rendered": "",
                "hallucination_check": "ERROR"
            }
