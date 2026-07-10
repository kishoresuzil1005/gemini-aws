from enum import Enum
from typing import Callable, Dict

class State(Enum):
    INIT = "INIT"
    READY = "READY"
    WORKING = "WORKING"
    WAITING = "WAITING"
    ERROR = "ERROR"
    TERMINATED = "TERMINATED"

class AgentStateMachine:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.current_state = State.INIT
        self.transitions: Dict[State, List[State]] = {
            State.INIT: [State.READY, State.ERROR],
            State.READY: [State.WORKING, State.TERMINATED, State.ERROR],
            State.WORKING: [State.READY, State.WAITING, State.ERROR],
            State.WAITING: [State.READY, State.WORKING, State.ERROR],
            State.ERROR: [State.READY, State.TERMINATED],
        }

    def transition_to(self, new_state: State) -> bool:
        if new_state in self.transitions.get(self.current_state, []):
            self.current_state = new_state
            return True
        return False
