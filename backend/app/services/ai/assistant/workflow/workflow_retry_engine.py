import time
import random
from app.services.ai.assistant.workflow.workflow_models import WorkflowStep

class WorkflowRetryEngine:
    def should_retry(self, step: WorkflowStep) -> bool:
        """Determines if a failed step is eligible for retry."""
        return step.retry_count < step.max_retries
        
    def get_backoff_delay(self, step: WorkflowStep) -> float:
        """Calculates exponential backoff with jitter."""
        base_delay = 2 ** step.retry_count
        jitter = random.uniform(0, 0.5 * base_delay)
        return base_delay + jitter
        
    def execute_with_retry(self, step: WorkflowStep, execution_func):
        """
        Wrapper to execute a function with intelligent retry logic.
        """
        while True:
            try:
                return execution_func(step)
            except Exception as e:
                step.error = str(e)
                if not self.should_retry(step):
                    raise
                    
                step.retry_count += 1
                delay = self.get_backoff_delay(step)
                time.sleep(delay)