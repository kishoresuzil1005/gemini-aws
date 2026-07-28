from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any
import datetime

class AuditLogger:
    """
    Enterprise audit logging for security compliance (SOC2 / HIPAA).
    Records WHO did WHAT, WHEN, and WHERE.
    """
    def log_activity(self, user_id: str, tenant_id: str, action: str, resource: str, status: str = "SUCCESS"):
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "status": status
        }
        # In a real environment, this gets written to an immutable append-only datastore or SIEM.
        logger.debug(f"[AuditLog] {json.dumps(log_entry) if 'json' in globals() else str(log_entry)}")
