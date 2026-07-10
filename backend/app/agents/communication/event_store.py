from typing import List, Dict, Any
from ..base.base_message import EventMessage

class EventStore:
    """
    Persistent store for all inter-agent events, enabling debugging,
    audit trails, and execution replay.
    """
    def __init__(self):
        self._events: List[EventMessage] = []

    def record_event(self, event: EventMessage):
        self._events.append(event)
        # In a real system, persist to a database or append-only log

    def get_events(self, limit: int = 100) -> List[EventMessage]:
        return self._events[-limit:]

    def get_events_by_type(self, event_type: str) -> List[EventMessage]:
        return [e for e in self._events if e.event_type == event_type]
