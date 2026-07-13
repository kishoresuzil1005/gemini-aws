"""
Node Sync — Production Implementation
Applies InventoryDiff results to Neo4j using the GraphTransaction.
"""
import logging
from typing import Any, Dict, List, Optional
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)


class NodeSync:
    """
    Syncs added, changed, and removed nodes to Neo4j.
    Does NOT call neo4j directly — operates through GraphTransaction for atomicity.
    """

    def __init__(self, neo4j_service: Neo4jService, transaction_manager: Any = None):
        self.neo4j = neo4j_service
        self.tx = transaction_manager  # GraphTransaction; if None, writes are immediate

    def sync_nodes(
        self,
        added: List[Dict[str, Any]],
        changed: List[Dict[str, Any]],
        removed: List[Dict[str, Any]],
    ) -> Dict[str, int]:
        counts = {"added": 0, "changed": 0, "removed": 0}

        # ─── Added nodes ─────────────────────────────────────────────────────────
        for resource in added:
            resource_id = resource.get("resource_id") or resource.get("id")
            if not resource_id:
                continue
            resource_type = resource.get("resource_type") or resource.get("type") or "Resource"
            name = resource.get("name") or resource_id
            provider = resource.get("provider", "AWS")
            region = resource.get("region", "")

            op = lambda r_id=resource_id, r_type=resource_type, r_name=name, prov=provider, reg=region: (
                self.neo4j.create_node(
                    node_type=r_type,
                    resource_id=r_id,
                    name=r_name,
                    provider=prov,
                    region=reg,
                )
            )

            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["added"] += 1
            logger.debug(f"Queued ADD node: {resource_id} ({resource_type})")

        # ─── Changed nodes ────────────────────────────────────────────────────────
        for resource in changed:
            resource_id = resource.get("resource_id") or resource.get("id")
            if not resource_id:
                continue
            resource_type = resource.get("resource_type") or resource.get("type") or "Resource"
            name = resource.get("name") or resource_id
            provider = resource.get("provider", "AWS")
            region = resource.get("region", "")

            op = lambda r_id=resource_id, r_type=resource_type, r_name=name, prov=provider, reg=region: (
                self.neo4j.create_node(
                    node_type=r_type,
                    resource_id=r_id,
                    name=r_name,
                    provider=prov,
                    region=reg,
                )
            )

            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["changed"] += 1
            logger.debug(f"Queued UPDATE node: {resource_id}")

        # ─── Removed nodes ────────────────────────────────────────────────────────
        for resource in removed:
            resource_id = resource.get("resource_id") or resource.get("id")
            if not resource_id:
                continue

            op = lambda r_id=resource_id: self._delete_node(r_id)

            if self.tx:
                self.tx.add_operation(op)
            else:
                op()
            counts["removed"] += 1
            logger.debug(f"Queued REMOVE node: {resource_id}")

        logger.info(f"NodeSync queued: +{counts['added']} ~{counts['changed']} -{counts['removed']}")
        return counts

    def _delete_node(self, resource_id: str):
        """Deletes a node and its relationships from Neo4j."""
        if self.neo4j.driver:
            query = "MATCH (n {id: $id}) DETACH DELETE n"
            try:
                with self.neo4j.driver.session() as session:
                    session.run(query, id=resource_id)
            except Exception as e:
                logger.error(f"Failed to delete node {resource_id}: {e}")
        else:
            # In-memory fallback
            from app.services.graph.neo4j_service import MemoryGraphStore
            MemoryGraphStore.nodes.pop(resource_id, None)
            MemoryGraphStore.edges = [
                e for e in MemoryGraphStore.edges
                if e["source"] != resource_id and e["target"] != resource_id
            ]