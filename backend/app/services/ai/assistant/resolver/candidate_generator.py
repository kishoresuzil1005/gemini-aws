import logging
import time
from typing import List, Dict, Any, Optional
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.orchestrator.cache import OrchestratorCache
from app.services.ai.context_engine.resolver import ResourceResolver
from app.services.ai.assistant.resolver.candidate_scorer import CandidateScorer
from app.core.logging import get_metrics_tracker

logger = logging.getLogger(__name__)

class CandidateGenerator:
    """Orchestrates candidate generation through Cache, PostgreSQL, and Neo4j."""
    
    def __init__(self):
        self.neo4j = Neo4jService()
        self.cache = OrchestratorCache(ttl=300)  # 5 minutes TTL
        self.postgres_resolver = ResourceResolver()
        self.scorer = CandidateScorer()
        
    def generate(self, entities: Dict[str, Any], session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Orchestrates candidate generation sequentially."""
        start_time = time.time()
        metrics = get_metrics_tracker()
        metrics.start("resolver_latency")
        
        candidates = []
        resource_ids = entities.get("resource_ids", [])
        keywords = entities.get("keywords", [])
        tag_filters = entities.get("tag_filters", {})
        
        # Track metric events
        resolver_cache_status = "MISS"
        postgres_status = "NO MATCH"
        neo4j_status = "SKIPPED"
        confidence_val = 0
        added_from_neo4j = 0
        
        # Determine identifier for trace
        identifier = resource_ids[0] if resource_ids else (keywords[0] if keywords else "unknown")
        
        # 1. Resolver Cache
        if session_id:
            search_terms = resource_ids or keywords[:3]
            if search_terms:
                cache_key = f"resolved:{session_id}:{':'.join(search_terms)}"
                cached = self.cache.get(cache_key)
                if cached:
                    resolver_cache_status = "HIT"
                    candidates = [cached]
                    confidence_val = 100
                    duration_ms = int((time.time() - start_time) * 1000)
                    
                    self._log_trace(session_id, identifier, resolver_cache_status, postgres_status, 
                                    confidence_val, neo4j_status, len(candidates), duration_ms)
                    return candidates
        
        # 2. PostgreSQL Inventory Search (Exact ID, ARN, Name, Tag)
        metrics.start("postgres_latency")
        pg_candidates = self.postgres_resolver.find_candidates(
            resource_ids=resource_ids,
            keywords=keywords,
            tag_filters=tag_filters
        )
        metrics.finish("postgres_latency")
        
        candidates.extend(pg_candidates)
        if candidates:
            postgres_status = "MATCH"
            
        # Score current candidates to see if we need Neo4j fallback
        temp_scored = self.scorer.score(candidates, entities)
        highest_confidence = temp_scored[0]["score"] * 100 if temp_scored else 0
        confidence_val = int(highest_confidence)
        
        # 3. Neo4j Relationship Lookup (Fallback if confidence < 95)
        if highest_confidence < 95 and (resource_ids or keywords):
            neo4j_status = "EXECUTED"
            try:
                metrics.start("neo4j_latency")
                if resource_ids:
                    records = self.neo4j.query(
                        "MATCH (n:AWSResource) WHERE n.id IN $ids OR n.arn IN $ids RETURN n.id AS id, n.name AS name, labels(n) AS type",
                        ids=resource_ids
                    )
                else:
                    records = self.neo4j.query(
                        "MATCH (n:AWSResource) WHERE ANY(word IN $words WHERE toLower(n.id) CONTAINS word OR toLower(coalesce(n.name, '')) CONTAINS word) RETURN n.id AS id, n.name AS name, labels(n) AS type LIMIT 15",
                        words=keywords
                    )
                metrics.finish("neo4j_latency")
                
                existing_ids = {c["id"] for c in candidates}
                for r in (records or []):
                    if r["id"] not in existing_ids:
                        candidates.append({
                            "id": r["id"],
                            "name": r.get("name"),
                            "type": r.get("type", []),
                            "source": "neo4j"
                        })
                        existing_ids.add(r["id"])
                        added_from_neo4j += 1
            except Exception as e:
                logger.error(f"Error querying Neo4j fallback: {e}")
                
        # Cache top candidate if found
        if candidates and session_id:
            final_scored = self.scorer.score(candidates, entities)
            if final_scored and final_scored[0]["score"] >= 0.80:
                search_terms = resource_ids or keywords[:3]
                if search_terms:
                    cache_key = f"resolved:{session_id}:{':'.join(search_terms)}"
                    self.cache.set(cache_key, final_scored[0])
                    
        duration_ms = int((time.time() - start_time) * 1000)
        metrics.finish("resolver_latency")
        
        self._log_trace(
            session_id=session_id or "none",
            identifier=identifier,
            cache_status=resolver_cache_status,
            postgres_status=postgres_status,
            confidence=confidence_val,
            neo4j_status=neo4j_status,
            candidate_count=len(candidates),
            duration_ms=duration_ms
        )

        return candidates
        
    def _log_trace(self, session_id: str, identifier: str, cache_status: str, postgres_status: str,
                   confidence: int, neo4j_status: str, candidate_count: int, duration_ms: int):
        """Outputs structured resolver tracing without raw queries."""
        if candidate_count == 0:
            trace = (
                "\nResolver Start\n\n"
                f"Cache:\n{cache_status}\n\n"
                f"Inventory:\n{postgres_status}\n\n"
                f"Neo4j:\n{neo4j_status}\n\n"
                f"Graph Candidates:\n0\n\n"
                f"Result:\nNOT FOUND\n\n"
                f"Duration:\n{duration_ms} ms\n"
            )
        else:
            trace = (
                "\nResolver Start\n\n"
                f"Session:\n{session_id}\n\n"
                f"Identifier:\n{identifier}\n\n"
                f"Cache:\n{cache_status}\n\n"
                f"PostgreSQL:\n{postgres_status}\n\n"
                f"Confidence:\n{confidence}\n\n"
                f"Neo4j:\n{neo4j_status}\n\n"
                f"Candidate Count:\n{candidate_count}\n\n"
                f"Duration:\n{duration_ms} ms\n"
            )
        logger.info(trace)
