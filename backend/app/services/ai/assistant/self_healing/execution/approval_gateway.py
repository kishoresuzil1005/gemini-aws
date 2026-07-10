from typing import Dict, Any, List
from datetime import datetime

class ApprovalGateway:
    """
    Manages human-in-the-loop approvals for sensitive or destructive self-healing actions.
    Provides API endpoints and notification hooks for the UX dashboard.
    """
    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    def request_approval(self, incident_id: str, plan: Dict[str, Any], reason: str) -> str:
        approval_id = f"app-{incident_id}"
        self.pending_approvals[approval_id] = {
            "incident_id": incident_id,
            "plan": plan,
            "reason": reason,
            "status": "PENDING",
            "requested_at": datetime.utcnow().isoformat()
        }
        print(f"[ApprovalGateway] Approval required for {incident_id}: {reason}")
        # In production, dispatch notification (Slack, Email) here
        return approval_id

    def resolve_approval(self, approval_id: str, approved: bool, user_id: str):
        if approval_id in self.pending_approvals:
            self.pending_approvals[approval_id]["status"] = "APPROVED" if approved else "REJECTED"
            self.pending_approvals[approval_id]["resolved_by"] = user_id
            self.pending_approvals[approval_id]["resolved_at"] = datetime.utcnow().isoformat()
            print(f"[ApprovalGateway] Request {approval_id} resolved: {'APPROVED' if approved else 'REJECTED'} by {user_id}")
