import os

COMMON_DIR = "backend/app/providers/common"
os.makedirs(COMMON_DIR, exist_ok=True)

files = {
    "transaction_manager.py": """
from typing import List, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class ProviderTransactionManager:
    \"\"\"
    Manages atomic operations across providers.
    Allows for commit and rollback to prevent half-modified infrastructure states.
    \"\"\"
    def __init__(self):
        self._operations: List[Dict[str, Any]] = []

    def add_operation(self, execute_fn: Callable, rollback_fn: Callable, description: str):
        self._operations.append({
            "execute": execute_fn,
            "rollback": rollback_fn,
            "description": description,
            "status": "pending"
        })

    def commit(self) -> bool:
        executed_ops = []
        for op in self._operations:
            logger.info(f"Executing: {op['description']}")
            try:
                op['execute']()
                op['status'] = "success"
                executed_ops.append(op)
            except Exception as e:
                logger.error(f"Transaction failed at step: {op['description']}. Error: {e}")
                self._rollback(executed_ops)
                return False
        
        self._operations.clear()
        return True

    def _rollback(self, executed_ops: List[Dict[str, Any]]):
        logger.warning("Initiating rollback for failed transaction...")
        for op in reversed(executed_ops):
            logger.info(f"Rolling back: {op['description']}")
            try:
                op['rollback']()
            except Exception as e:
                logger.critical(f"Rollback failed for {op['description']}. Manual intervention required! Error: {e}")
""",
    "relationship_diff.py": """
from typing import List, Dict, Any, Tuple

class RelationshipDiffEngine:
    \"\"\"
    Calculates differences between old graph relationships and new discovery relationships.
    Prevents rebuilding the Neo4j graph relationships from scratch.
    \"\"\"
    def calculate_diff(self, old_edges: List[Dict[str, Any]], new_edges: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        # Edges represented as { 'source': id, 'target': id, 'type': 'DEPENDS_ON' }
        def edge_signature(e):
            return f"{e.get('source')}_{e.get('type')}_{e.get('target')}"

        old_map = {edge_signature(e): e for e in old_edges}
        new_map = {edge_signature(e): e for e in new_edges}

        added = []
        removed = []
        changed = [] # Metadata on edges could change

        for sig, e_data in new_map.items():
            if sig not in old_map:
                added.append(e_data)
            elif old_map[sig] != e_data:
                changed.append(e_data)

        for sig, e_data in old_map.items():
            if sig not in new_map:
                removed.append(e_data)

        return {
            "added_edges": added,
            "removed_edges": removed,
            "changed_edges": changed
        }
""",
    "provider_snapshot.py": """
import json
import time
from typing import Dict, Any

class ProviderSnapshot:
    \"\"\"
    Captures the point-in-time state of provider infrastructure before major operations.
    \"\"\"
    def __init__(self, storage_path: str = "/tmp/snapshots"):
        self.storage_path = storage_path

    def take_snapshot(self, provider: str, inventory: Dict[str, Any]) -> str:
        snapshot_id = f"snap_{provider}_{int(time.time())}"
        # Save inventory payload to a file, S3, or database
        print(f"Captured snapshot {snapshot_id} for {provider}")
        return snapshot_id

    def get_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        # Retrieve snapshot payload
        return {}
""",
    "provider_checkpoint.py": """
from typing import Dict, Any

class ProviderCheckpoint:
    \"\"\"
    Used alongside the Transaction Manager to persist execution states 
    so long-running operations can be resumed.
    \"\"\"
    def __init__(self):
        self._checkpoints = {}

    def save_checkpoint(self, transaction_id: str, state: Dict[str, Any]):
        self._checkpoints[transaction_id] = state

    def load_checkpoint(self, transaction_id: str) -> Dict[str, Any]:
        return self._checkpoints.get(transaction_id, {})
""",
    "provider_profiler.py": """
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

class ProviderProfiler:
    \"\"\"
    Performance tuning and diagnostics for API latency.
    Tracks precise execution time of provider calls.
    \"\"\"
    @staticmethod
    def profile(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start
            
            logger.info(f"[PROFILER] {func.__name__} took {duration:.4f} seconds")
            return result
        return wrapper
"""
}

for filename, content in files.items():
    filepath = os.path.join(COMMON_DIR, filename)
    with open(filepath, 'w') as f:
        f.write(content.strip() + "\\n")
    print(f"Created {filepath}")
