import os
from typing import List, Dict, Any, Optional
from app.services.ai.embedding_service import EmbeddingService
from app.services.ai.qdrant_service import QdrantService
from app.services.ai.document_loader import DocumentLoader
from app.services.ai.ollama_service import OllamaService
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.retrieval_optimizer import RetrievalOptimizer
from app.services.ai.category_mapper import CategoryMapper
import logging

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, collection_name: str = "cloud_docs"):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService(collection_name=collection_name)
        self.document_loader = DocumentLoader()
        self.ollama_service = OllamaService()
        self.prompt_builder = PromptBuilder()
        self.retrieval_optimizer = RetrievalOptimizer(min_score=0.65)
        self.category_mapper = CategoryMapper()
        self._architecture_service = None

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
            logger.exception(f"Failed to index document: {e}")
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
                    logger.debug(f"Embedding chunk {i}/{total}")

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
            logger.exception(f"Failed to index directory: {e}")
            return 0

    def query_rag(self, query: str, limit: int = 8) -> Dict[str, Any]:
        """
        Retrieves matching chunks, optimizes context with RetrievalOptimizer, 
        and runs Ollama with the structured context.
        """
        try:
            INITIAL_RETRIEVAL = 20
            FINAL_CONTEXT = limit
            
            # Detect Intent and Categories
            intent = self.prompt_builder.detect_intent(query)
            architecture_mode = self.prompt_builder.is_architecture_question(query)
            target_categories = self.category_mapper.detect_categories(intent, query)
            
            logger.info(f"AI INTENT detected: {intent}")
            if architecture_mode:
                logger.info("AI MODE: Architecture")
            else:
                logger.info("AI MODE: Standard")
            
            # Generate search query embedding
            query_vector = self.embedding_service.get_embedding(query)
            
            # Retrieve nearest neighbors in primary categories
            matches = self.qdrant_service.search_similar(query_vector, limit=INITIAL_RETRIEVAL, categories=target_categories)
            
            # Fallback Strategy if insufficient results
            if len(matches) < 5:
                fallback_cats = self.category_mapper.get_fallback_categories(target_categories)
                if fallback_cats:
                    target_categories.extend(fallback_cats)
                    fallback_matches = self.qdrant_service.search_similar(query_vector, limit=INITIAL_RETRIEVAL, categories=fallback_cats)
                    # Merge unique
                    seen_ids = {m.get("id") for m in matches}
                    for fm in fallback_matches:
                        if fm.get("id") not in seen_ids:
                            matches.append(fm)
                            seen_ids.add(fm.get("id"))
                            
            # Optimize Context
            optimization_result = self.retrieval_optimizer.optimize(query, matches, final_k=FINAL_CONTEXT)
            optimized_chunks = optimization_result["optimized_chunks"]
            retrieval_stats = optimization_result["stats"]
            
            num_chunks = len(optimized_chunks)
            
            # Skip LLM if no valid chunks remain
            if num_chunks == 0:
                return {
                    "answer": "The retrieved documentation does not contain enough information.",
                    "intent": intent,
                    "architecture_mode": architecture_mode,
                    "confidence": 0.0,
                    "search": {
                        "categories": target_categories,
                        "documents_scanned": len(matches), # Approximation based on matches found
                        "chunks_found": len(matches),
                        "chunks_used": 0
                    },
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
            
            # Generate Architecture Context if applicable
            architecture_context = None
            if architecture_mode:
                if not self._architecture_service:
                    from app.services.ai.architecture_service import ArchitectureService
                    self._architecture_service = ArchitectureService()
                architecture_context = self._architecture_service.analyze(query)
                
            # Construct Prompt
            augmented_prompt = self.prompt_builder.build(
                query=query, 
                context=context_str, 
                architecture_context=architecture_context
            )
            
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
                "intent": intent,
                "architecture_mode": architecture_mode,
                "confidence": confidence,
                "search": {
                    "categories": target_categories,
                    "documents_scanned": len(matches),
                    "chunks_found": len(matches),
                    "chunks_used": num_chunks
                },
                "retrieval": retrieval_stats,
                "sources": references,
                "prompt_rendered": augmented_prompt,
                "hallucination_check": hallucination_status
            }
        except Exception as e:
            logger.exception(f"Failed during RAG query: {e}")
            return {
                "answer": f"I encountered an error retrieving or constructing the answer. Please verify connections. Details: {e}",
                "intent": "unknown",
                "architecture_mode": False,
                "confidence": 0.0,
                "search": {
                    "categories": [], "documents_scanned": 0, "chunks_found": 0, "chunks_used": 0
                },
                "retrieval": {
                    "retrieved": 0, "filtered": 0, "duplicates_removed": 0, "reranked": 0, "used": 0
                },
                "sources": [],
                "prompt_rendered": "",
                "hallucination_check": "ERROR"
            }