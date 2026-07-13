from typing import Dict, List, Any
from ..core.mission_events import MissionEvent, MissionEventType, MissionEventBus

class MissionTimeline:
    """
    Maintains a complete execution history and timeline of events for auditing and troubleshooting.
    """
    def __init__(self, event_bus: MissionEventBus):
        self._timelines: Dict[str, List[Dict[str, Any]]] = {}
        
        # Subscribe to all events
        for event_type in MissionEventType:
            event_bus.subscribe(event_type, self._record_event)

    def _record_event(self, event: MissionEvent):
        if event.mission_id not in self._timelines:
            self._timelines[event.mission_id] = []
            
        entry = {
            "timestamp": event.timestamp.isoformat(),
            "event": event.event_type.value,
            "details": event.details
        }
        self._timelines[event.mission_id].append(entry)
        print(f"[MissionTimeline] [{entry['timestamp']}] {event.mission_id} - {entry['event']}")

    def get_timeline(self, mission_id: str) -> List[Dict[str, Any]]:
        return self._timelines.get(mission_id, [])
        
    def export_timeline(self, mission_id: str) -> str:
        timeline = self.get_timeline(mission_id)
        if not timeline:
            return "No timeline found."
        
        output = [f"Timeline for {mission_id}:"]
        for entry in timeline:
            output.append(f"{entry['timestamp']} | {entry['event']} | {entry['details']}")
        return "\n".join(output