"""Audit Logger — Phase 4"""
from __future__ import annotations
import json, logging, time
from typing import Any, Dict, Optional

logger = logging.getLogger("cloudops.audit")


def log_ai_action(
    user_id: str,
    action: str,
    resource_id: Optional[str],
    intent: str,
    approved: bool,
    result: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    entry = {
        "ts": time.time(),
        "user": user_id,
        "action": action,
        "resource": resource_id,
        "intent": intent,
        "approved": approved,
        "result": result,
        "metadata": metadata or {},
    }
    logger.info("[AUDIT] %s", json.dumps(entry))
