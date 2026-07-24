# knowledge/snapshot/audit_manager.py
"""Tracks historical snapshot and rollback actions."""

from typing import List, Dict, Any
from datetime import datetime

class AuditManager:
    def __init__(self):
        self.audit_log: List[Dict[str, Any]] = []

    def record_action(self, action: str, snapshot_id: str, author: str, details: str = ""):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": action,
            "snapshot_id": snapshot_id,
            "author": author,
            "details": details
        }
        self.audit_log.append(entry)
