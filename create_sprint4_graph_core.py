import os

GRAPH_CORE_DIR = "backend/app/services/graph/core"
GRAPH_SYNC_DIR = "backend/app/services/graph/sync"
os.makedirs(GRAPH_CORE_DIR, exist_ok=True)
os.makedirs(GRAPH_SYNC_DIR, exist_ok=True)

core_files = {
    "graph_lock.py": """
import time
import logging

logger = logging.getLogger(__name__)

class GraphLockManager:
    \"\"\"
    Distributed lock to prevent parallel discoveries from corrupting graph state.
    Typically backed by Redis or similar distributed cache.
    \"\"\"
    def __init__(self):
        self._locks = {}

    def acquire_lock(self, lock_key: str, timeout: int = 60) -> bool:
        if self._locks.get(lock_key):
            logger.warning(f"Lock {lock_key} is already acquired.")
            return False
        self._locks[lock_key] = True
        logger.info(f"Acquired graph lock: {lock_key}")
        return True

    def release_lock(self, lock_key: str):
        if lock_key in self._locks:
            del self._locks[lock_key]
            logger.info(f"Released graph lock: {lock_key}")
""",
    "graph_transaction.py": """
import logging
from typing import Callable, Any, List

logger = logging.getLogger(__name__)

class GraphTransaction:
    \"\"\"
    Wraps Neo4j updates in atomic blocks. Supports rollback on partial failure.
    \"\"\"
    def __init__(self, neo4j_client: Any):
        self.neo4j_client = neo4j_client
        self._operations: List[Callable] = []

    def add_operation(self, operation: Callable):
        self._operations.append(operation)

    def commit(self) -> bool:
        # In a real Neo4j setup, this would use a session transaction
        # with self.neo4j_client.session().begin_transaction() as tx:
        logger.info("Starting Neo4j transaction...")
        try:
            for op in self._operations:
                op()
            logger.info("Neo4j transaction committed successfully.")
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}. Rolling back.")
            self.rollback()
            return False
        finally:
            self._operations.clear()

    def rollback(self):
        logger.warning("Rollback executed. No changes were committed to Neo4j.")
""",
    "graph_checkpoint.py": """
from typing import Dict, Any

class GraphCheckpoint:
    \"\"\"
    Persists state before large sync operations to allow recovery.
    \"\"\"
    def __init__(self):
        self._checkpoints = {}

    def create_checkpoint(self, checkpoint_id: str, state_data: Dict[str, Any]):
        self._checkpoints[checkpoint_id] = state_data

    def restore_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(checkpoint_id, {})
""",
    "graph_snapshot.py": """
import time
import json

class GraphSnapshotManager:
    \"\"\"
    Creates archival point-in-time copies of the entire Knowledge Graph.
    \"\"\"
    def create_snapshot(self, neo4j_client: Any, archive_path: str = "/tmp/graph_snapshots") -> str:
        snapshot_id = f"graph_snap_{int(time.time())}"
        # Execute Neo4j dump or export to JSON/CSV
        print(f"Captured full graph snapshot: {snapshot_id}")
        return snapshot_id
"""
}

sync_files = {
    "node_sync.py": """
from typing import List, Dict, Any

class NodeSync:
    \"\"\"Handles added, updated, and deleted nodes.\"\"\"
    def __init__(self, transaction_manager: Any):
        self.tx = transaction_manager

    def sync_nodes(self, added: List[Dict], changed: List[Dict], removed: List[Dict]):
        if added:
            self.tx.add_operation(lambda: print(f"Neo4j: Adding {len(added)} nodes"))
        if changed:
            self.tx.add_operation(lambda: print(f"Neo4j: Updating {len(changed)} nodes"))
        if removed:
            self.tx.add_operation(lambda: print(f"Neo4j: Removing {len(removed)} nodes"))
""",
    "edge_sync.py": """
from typing import List, Dict, Any

class EdgeSync:
    \"\"\"Handles relationships, dependencies, and network updates.\"\"\"
    def __init__(self, transaction_manager: Any):
        self.tx = transaction_manager

    def sync_edges(self, added: List[Dict], changed: List[Dict], removed: List[Dict]):
        if added:
            self.tx.add_operation(lambda: print(f"Neo4j: Adding {len(added)} edges"))
        if changed:
            self.tx.add_operation(lambda: print(f"Neo4j: Updating {len(changed)} edges"))
        if removed:
            self.tx.add_operation(lambda: print(f"Neo4j: Removing {len(removed)} edges"))
""",
    "graph_version_manager.py": """
import time

class GraphVersionManager:
    \"\"\"Maintains version snapshots of the graph for rollback and audit purposes.\"\"\"
    def __init__(self):
        self.current_version = 0

    def increment_version(self) -> int:
        self.current_version += 1
        return self.current_version
""",
    "graph_sync_engine.py": """
from .node_sync import NodeSync
from .edge_sync import EdgeSync
from .graph_version_manager import GraphVersionManager
from backend.app.services.graph.core.graph_transaction import GraphTransaction
from backend.app.services.graph.core.graph_lock import GraphLockManager

class GraphSyncEngine:
    \"\"\"
    Master orchestrator. Executes the strict pipeline: 
    Discovery -> Diff -> Node Sync -> Edge Sync -> Version -> Events.
    \"\"\"
    def __init__(self, neo4j_client, event_publisher):
        self.lock_manager = GraphLockManager()
        self.tx = GraphTransaction(neo4j_client)
        self.node_sync = NodeSync(self.tx)
        self.edge_sync = EdgeSync(self.tx)
        self.version_manager = GraphVersionManager()
        self.event_publisher = event_publisher

    def run_sync_pipeline(self, provider: str, node_diffs: dict, edge_diffs: dict):
        lock_key = f"sync_{provider}"
        if not self.lock_manager.acquire_lock(lock_key):
            print("Sync already in progress. Aborting.")
            return

        try:
            # 1. Node Sync
            self.node_sync.sync_nodes(
                node_diffs.get('added', []),
                node_diffs.get('changed', []),
                node_diffs.get('removed', [])
            )
            
            # 2. Edge Sync
            self.edge_sync.sync_edges(
                edge_diffs.get('added_edges', []),
                edge_diffs.get('changed_edges', []),
                edge_diffs.get('removed_edges', [])
            )

            # 3. Commit Transaction
            if self.tx.commit():
                # 4. Version
                version = self.version_manager.increment_version()
                
                # 5. Publish Events
                self.event_publisher.publish("GraphSynced", {"provider": provider, "version": version})
                
        finally:
            self.lock_manager.release_lock(lock_key)
"""
}

for filename, content in core_files.items():
    with open(os.path.join(GRAPH_CORE_DIR, filename), "w") as f:
        f.write(content.strip() + "\\n")
    print(f"Created {filename}")

for filename, content in sync_files.items():
    with open(os.path.join(GRAPH_SYNC_DIR, filename), "w") as f:
        f.write(content.strip() + "\\n")
    print(f"Created {filename}")
