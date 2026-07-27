"""
Evidence Collector — Phase 2
==============================
Pulls raw evidence from providers and attaches it to an InvestigationSession.
"""

from __future__ import annotations

import logging
from typing import Optional

from .session import InvestigationSession

logger = logging.getLogger(__name__)


class EvidenceCollector:
    """
    Coordinates evidence gathering from multiple providers
    and stores results in the investigation session.
    """

    def collect_all(self, session: InvestigationSession, resource_id: Optional[str] = None) -> None:
        rid = resource_id or session.root_resource_id
        if not rid:
            logger.warning("[EvidenceCollector] No resource ID provided")
            return

        self._collect_inventory(session, rid)
        self._collect_graph(session, rid)
        self._collect_metrics(session, rid)
        self._collect_security(session, rid)

    def _collect_inventory(self, session: InvestigationSession, rid: str) -> None:
        try:
            from app.database import SessionLocal
            from app.models import ResourceDB
            db = SessionLocal()
            try:
                row = db.query(ResourceDB).filter(ResourceDB.resource_id == rid).first()
                if row:
                    session.add_evidence(
                        source="inventory",
                        data={"id": row.resource_id, "type": row.resource_type,
                              "name": row.name, "region": row.region, "status": row.status},
                        confidence=0.95,
                    )
                    session.add_timeline("provider_result", f"Inventory: {row.resource_type} {row.name}")
            finally:
                db.close()
        except Exception as e:
            logger.debug("[EvidenceCollector] Inventory: %s", e)

    def _collect_graph(self, session: InvestigationSession, rid: str) -> None:
        try:
            from app.services.graph.neo4j_service import Neo4jService
            neo4j = Neo4jService()
            cypher = """
            MATCH (n:Resource {resource_id: $rid})-[r]->(m:Resource)
            RETURN m.resource_id AS target, type(r) AS rel, m.name AS name
            LIMIT 20
            """
            records = neo4j.query(cypher, rid=rid)
            if records:
                session.add_evidence(source="graph", data={"relationships": records}, confidence=0.90)
                session.add_timeline("provider_result", f"Graph: {len(records)} relationships found")
        except Exception as e:
            logger.debug("[EvidenceCollector] Graph: %s", e)

    def _collect_metrics(self, session: InvestigationSession, rid: str) -> None:
        session.add_timeline("provider_result", "Metrics: provider pending integration")

    def _collect_security(self, session: InvestigationSession, rid: str) -> None:
        session.add_timeline("provider_result", "Security: provider pending integration")
