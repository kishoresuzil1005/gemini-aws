from enum import Enum
from typing import Dict, Any

class HealingState(str, Enum):
    DETECTED = "DETECTED"
    DIAGNOSING = "DIAGNOSING"
    PLANNING = "PLANNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    EXECUTING = "EXECUTING"
    VERIFYING = "VERIFYING"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    ROLLBACK = "ROLLBACK"
    COMPLETED = "COMPLETED"

class HealingStateMachine:
    """
    Tracks and enforces state transitions for an ongoing self-healing incident.
    """
    def __init__(self):
        self._states: Dict[str, HealingState] = {}

    def transition(self, incident_id: str, new_state: HealingState):
        print(f"[HealingStateMachine] Incident {incident_id} transitioned to {new_state.value}")
        self._states[incident_id] = new_state
        
    def get_state(self, incident_id: str) -> HealingState:
        return self._states.get(incident_id, HealingState.DETECTED)
