from enum import Enum
from typing import Dict, List, Callable, Any
from datetime import datetime

class MissionEventType(str, Enum):
    MISSION_CREATED = "MISSION_CREATED"
    MISSION_STARTED = "MISSION_STARTED"
    MISSION_PAUSED = "MISSION_PAUSED"
    MISSION_RESUMED = "MISSION_RESUMED"
    MISSION_CANCELLED = "MISSION_CANCELLED"
    MISSION_COMPLETED = "MISSION_COMPLETED"
    MISSION_FAILED = "MISSION_FAILED"
    OBJECTIVE_COMPLETED = "OBJECTIVE_COMPLETED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"

class MissionEvent:
    def __init__(self, event_type: MissionEventType, mission_id: str, details: Dict[str, Any] = None):
        self.event_type = event_type
        self.mission_id = mission_id
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class MissionEventBus:
    """
    Event-driven lifecycle notifications for missions. Components subscribe 
    to events instead of polling the repository.
    """
    def __init__(self):
        self.subscribers: Dict[MissionEventType, List[Callable]] = {}

    def subscribe(self, event_type: MissionEventType, callback: Callable[[MissionEvent], None]):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)

    def publish(self, event: MissionEvent):
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[MissionEventBus] Error in subscriber: {e}")