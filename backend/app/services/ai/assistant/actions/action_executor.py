import time
from typing import Optional
from app.providers.provider_registry import ProviderRegistry
from app.services.ai.assistant.actions.action_models import ActionPlan, ActionStatus, ExecutionResult
from app.services.ai.assistant.actions.action_state_machine import ActionStateMachine

class ActionExecutor:
    def __init__(self, provider_registry: ProviderRegistry, state_machine: ActionStateMachine):
        self.provider_registry = provider_registry
        self.state_machine = state_machine

    def execute(self, plan: ActionPlan) -> ExecutionResult:
        """
        Actually executes the validated and approved ActionPlan.
        Never calls AWS directly. Delegates to the registered provider.
        """
        provider_name = plan.request.context.provider_name
        provider = self.provider_registry.get_provider(provider_name)
        
        if not provider:
            self.state_machine.transition(plan, ActionStatus.FAILED)
            return ExecutionResult(
                provider_status="ERROR",
                latency_ms=0,
                raw_response={},
                error=f"Provider '{provider_name}' not found."
            )
            
        start_time = time.time()
        self.state_machine.transition(plan, ActionStatus.EXECUTING)
        try:
            raw_response = provider.execute_action(
                action=plan.request.action_name,
                resource_id=plan.request.resource_id,
                **plan.request.parameters
            )
            latency = int((time.time() - start_time) * 1000)
            
            self.state_machine.transition(plan, ActionStatus.COMPLETED)
            return ExecutionResult(
                provider_status="SUCCESS",
                latency_ms=latency,
                raw_response=raw_response
            )
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            self.state_machine.transition(plan, ActionStatus.FAILED)
            return ExecutionResult(
                provider_status="FAILED",
                latency_ms=latency,
                raw_response={},
                error=str(e)
            