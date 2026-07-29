"""
Multi-Source Resolver — Phase 1 / Phase 4
==========================================
Searches for a resource through an ordered chain of sources,
returning early when confidence is high enough.

Source chain (in order):
  1. Redis session cache
  2. Conversation memory (last selected resource)
  3. PostgreSQL inventory (exact ID / ARN / name)
  4. Neo4j Graph (relationship-aware lookup)
  5. AWS metadata (boto3 describe calls — only if ID looks valid)
  6. Tag store (Postgres tag search)
  7. Neo4j full-text search (fuzzy name match)
  8. Qdrant semantic search (embeddings — optional)
"""

from __future__ import annotations

import logging
import re
from typing import List, Optional

from app.services.ai.orchestrator.cache import OrchestratorCache
from app.services.ai.orchestrator.models import (
    CloudProvider,
    CandidateQuery,
    Resource,
    ResourceStatus,
    ResolvedResource,
)
from .confidence_engine import ConfidenceEngine, ResolutionDecision, ConfidenceResult

logger = logging.getLogger(__name__)

_HIGH_CONFIDENCE_THRESHOLD = 0.93


class MultiSourceResolver:
    """
    @deprecated
    Legacy Compatibility Wrapper
    Chains multiple resolution strategies and returns a ranked
    list of ResolvedResource candidates.
    """

    def __init__(self, cache: Optional[OrchestratorCache] = None):
        self._cache = cache or OrchestratorCache()
        self._confidence = ConfidenceEngine()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def resolve(
        self,
        query: CandidateQuery,
        session_id: Optional[str] = None,
        conversation_resource: Optional[str] = None,
    ) -> ConfidenceResult:
        """
        Run all resolution strategies and return a ConfidenceResult.

        Args:
            query:                Structured query from EntityExtractor.
            session_id:           Active session ID for cache lookup.
            conversation_resource: Last resource from conversation memory.
        Returns:
            ConfidenceResult with decision and ranked candidates.
        """
        candidates: List[ResolvedResource] = []

        # ---- Strategy 1: Redis Cache ----
        if session_id:
            cached = self._from_cache(query, session_id)
            candidates.extend(cached)
            if self._early_exit(candidates):
                logger.info("[Resolver] Early exit from Redis cache")
                return self._confidence.score(candidates)

        # ---- Strategy 2: Conversation Memory ----
        if conversation_resource:
            mem_candidates = self._from_memory(conversation_resource, query)
            candidates.extend(mem_candidates)
            if self._early_exit(candidates):
                logger.info("[Resolver] Early exit from conversation memory")
                return self._confidence.score(candidates)

        # ---- Strategy 3: Exact ID / ARN ----
        if query.resource_ids:
            exact = self._from_explicit_ids(query.resource_ids)
            candidates.extend(exact)
            if self._early_exit(candidates):
                logger.info("[Resolver] Early exit from explicit IDs")
                return self._confidence.score(candidates)

        # ---- Strategy 4: PostgreSQL Inventory ----
        db_results = self._from_postgres(query)
        candidates.extend(db_results)
        if self._early_exit(candidates):
            logger.info("[Resolver] Early exit from Postgres")
            return self._confidence.score(candidates)

        # ---- Strategy 5: Neo4j Graph ----
        graph_results = self._from_neo4j(query)
        candidates.extend(graph_results)
        if self._early_exit(candidates):
            logger.info("[Resolver] Early exit from Neo4j")
            return self._confidence.score(candidates)

        # ---- Strategy 6: Tag Store ----
        if query.tag_filters:
            tag_results = self._from_tags(query)
            candidates.extend(tag_results)

        logger.info("[Resolver] Total candidates: %d", len(candidates))
        return self._confidence.score(candidates)

    # ------------------------------------------------------------------
    # Strategies
    # ------------------------------------------------------------------

    def _from_cache(self, query: CandidateQuery, session_id: str) -> List[ResolvedResource]:
        try:
            key = f"resolved:{session_id}:{':'.join(query.resource_ids or query.tokens[:3])}"
            cached = self._cache.get(key)
            if cached and isinstance(cached, dict):
                r = Resource(
                    id=cached.get("id", ""),
                    provider=CloudProvider(cached.get("provider", "aws")),
                    service=cached.get("service", ""),
                    type=cached.get("type", ""),
                    name=cached.get("name"),
                )
                return [ResolvedResource(resource=r, confidence=1.0, source="redis_cache")]
        except Exception as e:
            logger.debug("[Resolver] Cache lookup failed: %s", e)
        return []

    def _from_memory(self, resource_id: str, query: CandidateQuery) -> List[ResolvedResource]:
        """Use conversation-memory resource when pronouns (it/this/that) are detected."""
        pronouns = {"it", "this", "that", "them", "they", "those", "the instance", "the server"}
        if any(p in query.raw_input.lower() for p in pronouns):
            r = Resource(
                id=resource_id,
                provider=CloudProvider.AWS,
                service=self._guess_service(resource_id),
                type="instance",
            )
            return [ResolvedResource(resource=r, confidence=0.95, source="conversation_memory")]
        return []

    def _from_explicit_ids(self, ids: List[str]) -> List[ResolvedResource]:
        results = []
        for rid in ids:
            r = Resource(
                id=rid,
                provider=CloudProvider.AWS,
                service=self._guess_service(rid),
                type=self._guess_type(rid),
            )
            results.append(ResolvedResource(resource=r, confidence=0.95, source="regex"))
        return results

    def _from_postgres(self, query: CandidateQuery) -> List[ResolvedResource]:
        try:
            from app.database import SessionLocal
            from app.models import ResourceDB
            db = SessionLocal()
            try:
                results = []
                for token in (query.resource_ids or query.tokens[:5]):
                    rows = (
                        db.query(ResourceDB)
                        .filter(
                            (ResourceDB.resource_id.ilike(f"%{token}%")) |
                            (ResourceDB.name.ilike(f"%{token}%"))
                        )
                        .limit(5)
                        .all()
                    )
                    for row in rows:
                        r = Resource(
                            id=row.resource_id,
                            provider=CloudProvider.AWS,
                            service=(row.resource_type or "").lower(),
                            type=(row.resource_type or "").lower(),
                            name=row.name,
                            region=row.region,
                            status=ResourceStatus(row.status.lower()) if row.status else ResourceStatus.UNKNOWN,
                        )
                        results.append(ResolvedResource(resource=r, confidence=0.88, source="postgres"))
                return results
            finally:
                db.close()
        except Exception as e:
            logger.debug("[Resolver] Postgres lookup failed: %s", e)
        return []

    def _from_neo4j(self, query: CandidateQuery) -> List[ResolvedResource]:
        try:
            from app.services.graph.neo4j_service import Neo4jService
            neo4j = Neo4jService()
            search_terms = query.resource_ids or query.tokens[:5]
            if not search_terms:
                return []
            cypher = """
            MATCH (n:Resource)
            WHERE ANY(word IN $words WHERE
                toLower(n.resource_id) CONTAINS word OR
                toLower(coalesce(n.name, '')) CONTAINS word OR
                toLower(coalesce(n.resource_type, '')) CONTAINS word)
            RETURN n.resource_id AS id,
                   n.name AS name,
                   n.resource_type AS type,
                   n.region AS region
            LIMIT 5
            """
            records = neo4j.query(cypher, words=search_terms)
            results = []
            for rec in (records or []):
                r = Resource(
                    id=rec.get("id", ""),
                    provider=CloudProvider.AWS,
                    service=(rec.get("type") or "").lower(),
                    type=(rec.get("type") or "").lower(),
                    name=rec.get("name"),
                    region=rec.get("region"),
                )
                results.append(ResolvedResource(resource=r, confidence=0.82, source="neo4j"))
            return results
        except Exception as e:
            logger.debug("[Resolver] Neo4j lookup failed: %s", e)
        return []

    def _from_tags(self, query: CandidateQuery) -> List[ResolvedResource]:
        try:
            from app.database import SessionLocal
            from app.models import ResourceDB
            db = SessionLocal()
            try:
                results = []
                # Simple tag search via Postgres JSON field if available
                for tag_key, tag_val in query.tag_filters.items():
                    rows = db.query(ResourceDB).filter(
                        ResourceDB.tags.astext.contains(tag_val)
                    ).limit(5).all()
                    for row in rows:
                        r = Resource(
                            id=row.resource_id,
                            provider=CloudProvider.AWS,
                            service=(row.resource_type or "").lower(),
                            type=(row.resource_type or "").lower(),
                            name=row.name,
                        )
                        results.append(ResolvedResource(resource=r, confidence=0.78, source="tag_store"))
                return results
            finally:
                db.close()
        except Exception as e:
            logger.debug("[Resolver] Tag store lookup failed: %s", e)
        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _early_exit(candidates: List[ResolvedResource]) -> bool:
        return bool(candidates and candidates[0].confidence >= _HIGH_CONFIDENCE_THRESHOLD)

    @staticmethod
    def _guess_service(resource_id: str) -> str:
        rid = resource_id.lower()
        if rid.startswith("i-"):       return "ec2"
        if rid.startswith("vpc-"):     return "vpc"
        if rid.startswith("sg-"):      return "ec2"
        if rid.startswith("subnet-"):  return "vpc"
        if rid.startswith("vol-"):     return "ebs"
        if rid.startswith("snap-"):    return "ebs"
        if "rds" in rid:               return "rds"
        if "lambda" in rid:            return "lambda"
        if ":s3:" in rid:              return "s3"
        return "unknown"

    @staticmethod
    def _guess_type(resource_id: str) -> str:
        rid = resource_id.lower()
        if rid.startswith("i-"):       return "instance"
        if rid.startswith("vpc-"):     return "vpc"
        if rid.startswith("sg-"):      return "security_group"
        if rid.startswith("subnet-"):  return "subnet"
        if rid.startswith("vol-"):     return "volume"
        return "resource"
