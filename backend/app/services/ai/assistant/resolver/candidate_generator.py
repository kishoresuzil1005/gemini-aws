import logging
from typing import List, Dict, Any, Optional
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.orchestrator.cache import OrchestratorCache
from app.services.ai.context_engine.resolver import ResourceResolver
from app.services.ai.assistant.resolver.candidate_scorer import CandidateScorer

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
        candidates = []
        resource_ids = entities.get("resource_ids", [])
        keywords = entities.get("keywords", [])
        tag_filters = entities.get("tag_filters", {})
        
        # 1. Resolver Cache
        if session_id:
            search_terms = resource_ids or keywords[:3]
            if search_terms:
                cache_key = f"resolved:{session_id}:{':'.join(search_terms)}"
                cached = self.cache.get(cache_key)
                if cached:
                    logger.info(f"Resolver Stage: Cache HIT. Duration: 2 ms. Result: FOUND")
                    return [cached]
        
        # 2. PostgreSQL Inventory Search (Exact ID, ARN, Name, Tag)
        start_time = logging.Formatter.converter()
        pg_candidates = self.postgres_resolver.find_candidates(
            resource_ids=resource_ids,
            keywords=keywords,
            tag_filters=tag_filters
        )
        
        candidates.extend(pg_candidates)
        
        # Score current candidates to see if we need Neo4j fallback
        temp_scored = self.scorer.score(candidates, entities)
        highest_confidence = temp_scored[0]["score"] * 100 if temp_scored else 0
        
        logger.info(f"Resolver Stage: Inventory Lookup. Cache: MISS. Confidence: {highest_confidence}. Result: {'FOUND' if candidates else 'NOT_FOUND'}")
        
        # 3. Neo4j Relationship Lookup (Fallback if confidence < 95)
        if highest_confidence < 95 and (resource_ids or keywords):
            logger.info(f"Neo4j Query Reason: Inventory confidence = {highest_confidence}. Purpose: Relationship fallback.")
            try:
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
                
                existing_ids = {c["id"] for c in candidates}
                added_from_neo4j = 0
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
                logger.info(f"Neo4j Query Nodes: {added_from_neo4j}. Relationships: 0.")
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

        return candidates
