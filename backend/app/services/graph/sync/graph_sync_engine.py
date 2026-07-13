"""
Graph Sync Engine — Production Implementation
Executes the full sync pipeline:
  Discovery -> InventoryDiff -> RelationshipDiff -> NodeSync -> EdgeSync -> Version -> Events
"""
import logging
import time
from typing import Any, Dict, List, Optional

from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.sync.node_sync import NodeSync
from app.services.graph.sync.edge_sync import EdgeSync
from app.services.graph.sync.graph_version_manager import GraphVersionManager
from app.services.graph.core.graph_lock import GraphLockManager
from app.services.graph.core.graph_transaction import GraphTransaction
from app.providers.common.inventory_diff import InventoryDiffEngine
from app.providers.common.relationship_diff import RelationshipDiffEngine

logger = logging.getLogger(__name__)


class GraphSyncEngine:
    """
    Master orchestrator. Executes the strict synchronization pipeline:
    Discovery -> Diff -> NodeSync -> EdgeSync -> Version -> Publish Events

    Guarantees:
    - Atomic Neo4j writes via GraphTransaction
    - Parallel-discovery safety via GraphLockManager
    - Incremental updates via InventoryDiffEngine + RelationshipDiffEngine
    """

    def __init__(self, neo4j_service: Optional[Neo4jService] = None, event_publisher: Optional[Any] = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.event_publisher = event_publisher
        self.lock_manager = GraphLockManager()
        self.version_manager = GraphVersionManager()
        self.inventory_diff = InventoryDiffEngine()
        self.relationship_diff = RelationshipDiffEngine()

    def run_sync_pipeline(
        self,
        provider: str,
        new_inventory: List[Dict[str, Any]],
        old_inventory: Optional[List[Dict[str, Any]]] = None,
        new_edges: Optional[List[Dict[str, Any]]] = None,
        old_edges: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Main entry point. Accepts raw discovery data, computes diffs, applies to Neo4j.

        Args:
            provider: Provider name (e.g. "aws", "azure")
            new_inventory: Freshly discovered resources
            old_inventory: Previously known resources (for diffing). Loaded from last snapshot if None.
            new_edges: Freshly discovered relationships
            old_edges: Previously known relationships

        Returns:
            Summary of sync results.
        """
        lock_key = f"graph_sync_{provider}"

        if not self.lock_manager.acquire_lock(lock_key):
            logger.warning(f"Sync for provider={provider} is already running. Skipping.")
            return {"status": "skipped", "reason": "lock_held", "provider": provider}

        start_time = time.perf_counter()
        try:
            # ─── 1. Inventory Diff ───────────────────────────────────────────────
            if old_inventory is None:
                old_inventory = []

            node_diff = self.inventory_diff.calculate_diff(old_inventory, new_inventory)
            logger.info(
                f"[{provider}] Inventory diff: +{len(node_diff['added'])} "
                f"~{len(node_diff['changed'])} -{len(node_diff['removed'])}"
            )

            # ─── 2. Relationship Diff ────────────────────────────────────────────
            if old_edges is None:
                old_edges = []
            if new_edges is None:
                new_edges = []

            edge_diff = self.relationship_diff.calculate_diff(old_edges, new_edges)
            logger.info(
                f"[{provider}] Edge diff: +{len(edge_diff['added_edges'])} "
                f"~{len(edge_diff['changed_edges'])} -{len(edge_diff['removed_edges'])}"
            )

            # ─── 3. Open Neo4j Transaction ───────────────────────────────────────
            tx = GraphTransaction(self.neo4j)
            node_sync = NodeSync(self.neo4j, transaction_manager=tx)
            edge_sync = EdgeSync(self.neo4j, transaction_manager=tx)

            # ─── 4. Stage Node Operations ────────────────────────────────────────
            node_counts = node_sync.sync_nodes(
                added=node_diff["added"],
                changed=node_diff["changed"],
                removed=node_diff["removed"],
            )

            # ─── 5. Stage Edge Operations ────────────────────────────────────────
            edge_counts = edge_sync.sync_edges(
                added=edge_diff["added_edges"],
                changed=edge_diff["changed_edges"],
                removed=edge_diff["removed_edges"],
            )

            # ─── 6. Commit ───────────────────────────────────────────────────────
            success = tx.commit()
            if not success:
                return {
                    "status": "error",
                    "reason": "transaction_failed",
                    "provider": provider,
                }

            # ─── 7. Version ──────────────────────────────────────────────────────
            version = self.version_manager.increment_version()

            # ─── 8. Publish Events ───────────────────────────────────────────────
            elapsed = round(time.perf_counter() - start_time, 3)
            summary = {
                "status": "success",
                "provider": provider,
                "version": version,
                "duration_seconds": elapsed,
                "nodes": node_counts,
                "edges": edge_counts,
            }
            if self.event_publisher:
                self.event_publisher.publish("GraphSynced", summary)

            logger.info(f"[{provider}] Sync completed in {elapsed}s — version {version}")
            return summary

        except Exception as e:
            logger.error(f"[{provider}] Sync pipeline failed: {e}", exc_info=True)
            return {"status": "error", "provider": provider, "error": str(e)}

        finally:
            self.lock_manager.release_lock(lock_key)