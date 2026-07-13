"""
Edge Sync — Production Implementation
Applies RelationshipDiff results to Neo4j using the GraphTransaction.
"""
import logging
from typing import Any, Dict, List, Optional
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class EdgeSync:
    """
    Syncs added, changed, and removed edges to Neo4j.
    Edges are represented as { source, target, type } dicts.
    """

    def __init__(self, neo4j_service: Neo4jService, transaction_manager: Any = None):
        self.neo4j = neo4j_service
        self.tx = transaction_manager

    def sync_edges(
        self,
        added: List[Dict[str, Any]],
        changed: List[Dict[str, Any]],
        removed: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        counts = {"added": 0, "changed": 0, "removed": 0}

        # ─── Added edges ─────────────────────────────────────────────────────────
        for edge in added:
            source = edge.get("source")
            target = edge.get("target")
            rel_type = edge.get("type", "RELATED_TO")
            if not source or not target:
                continue

            op = lambda s=source, t=target, r=rel_type: self.neo4j.create_relationship(
                source_id=s, target_id=t, relationship_type=r
            )
            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["added"] += 1
            logger.debug(f"Queued ADD edge: ({source})-[{rel_type}]->({target})")

        # ─── Changed edges (re-MERGE) ─────────────────────────────────────────────
        for edge in changed:
            source = edge.get("source")
            target = edge.get("target")
            rel_type = edge.get("type", "RELATED_TO")
            if not source or not target:
                continue

            op = lambda s=source, t=target, r=rel_type: self.neo4j.create_relationship(
                source_id=s, target_id=t, relationship_type=r
            )
            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["changed"] += 1

        # ─── Removed edges ────────────────────────────────────────────────────────
        for edge in removed:
            source = edge.get("source")
            target = edge.get("target")
            rel_type = edge.get("type", "RELATED_TO")
            if not source or not target:
                continue

            op = lambda s=source, t=target, r=rel_type: self._delete_edge(s, t, r)
            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["removed"] += 1
            logger.debug(f"Queued REMOVE edge: ({source})-[{rel_type}]->({target})")

        logger.info(f"EdgeSync queued: +{counts['added']} ~{counts['changed']} -{counts['removed']}")
        return counts

    def _delete_edge(self, source_id: str, target_id: str, rel_type: str):
        """Deletes a specific relationship from Neo4j."""
        safe_rel = "".join(c for c in rel_type if c.isalnum() or c == "_").upper() or "RELATED_TO"
        if self.neo4j.driver:
            query = f"""
            MATCH (a {{id: $source}})-[r:{safe_rel}]->(b {{id: $target}})
            DELETE r
            """
            try:
                with self.neo4j.driver.session() as session:
                    session.run(query, source=source_id, target=target_id)
            except Exception as e:
                logger.error(f"Failed to delete edge ({source_id})-[{safe_rel}]->({target_id}): {e}")
        else:
            from app.services.graph.neo4j_service import MemoryGraphStore
            MemoryGraphStore.edges = [
                e for e in MemoryGraphStore.edges
                if not (e["source"] == source_id and e["target"] == target_id and e["type"] == safe_rel)
            ]