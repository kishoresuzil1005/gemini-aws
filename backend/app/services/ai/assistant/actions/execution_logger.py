from typing import List
from app.services.ai.assistant.actions.action_models import ActionPlan, ExecutionResult, ExecutionLog

class ExecutionLogger:
    def __init__(self):
        self.logs: List[ExecutionLog] = []

    def log_execution(self, plan: ActionPlan, result: ExecutionResult):
        """
        Records the technical execution metadata.
        """
        log = ExecutionLog(
            action=plan.request.action_name,
            resource=plan.request.resource_id,
            execution_time_ms=result.latency_ms,
            result=result.provider_status,
            errors=[result.error] if result.error else [],
            retries=0, # Simplified for now
            provider=plan.request.context.provider_name
        )
        self.logs.append(log)
        # Real system would write to CloudWatch or Elasticsearch her