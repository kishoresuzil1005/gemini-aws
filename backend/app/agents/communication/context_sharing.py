from typing import Dict, Any

class ContextSharingEngine:
    """
    Provides a synchronized, distributed context that agents can read from 
    and write to. Allows sharing results from earlier subtasks.
    """
    def __init__(self):
        self._shared_contexts: Dict[str, Dict[str, Any]] = {}

    def get_context(self, workflow_id: str) -> Dict[str, Any]:
        if workflow_id not in self._shared_contexts:
            self._shared_contexts[workflow_id] = {}
        return self._shared_contexts[workflow_id]

    def update_context(self, workflow_id: str, key: str, value: Any):
        context = self.get_context(workflow_id)
        context[key] = value

    def clear_context(self, workflow_id: str):
        if workflow_id in self._shared_contexts:
            del self._shared_contexts[workflow_id]
