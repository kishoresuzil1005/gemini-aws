from typing import List, Optional
from app.services.ai.assistant.actions.action_models import ActionPlan, ApprovalResult, ExecutionResult, RollbackPlan, AuditRecord

class AuditEngine:
    def __init__(self):
        self.records: List[AuditRecord] = []

    def record_audit(
        self, 
        plan: ActionPlan, 
        approval: Optional[ApprovalResult], 
        execution: Optional[ExecutionResult], 
        rollback: Optional[RollbackPlan]
    ):
        """
        Emits permanent compliance records.
        """
        record = AuditRecord(
            who=plan.request.context.user_id or "SYSTEM",
            why=plan.request.context.correlation_id,
            action=plan.request.action_name,
            resource=plan.request.resource_id,
            approval_proof=approval.approver if approval else "NONE_REQUIRED",
            execution_proof="SUCCESS" if execution and not execution.error else "FAILED",
            rollback_plan=rollback,
            status=plan.status.value
        )
        self.records.append(record)
        # Real system would write to immutable ledger or S3 here
