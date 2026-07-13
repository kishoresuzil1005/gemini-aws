from typing import Dict, Any, List
from datetime import datetime

class HealingTimeline:
    """
    Maintains an audit trail of the self-healing progression for operations dashboards.
    """
    def __init__(self):
        self._timeline: Dict[str, List[Dict[str, Any]]] = {}

    def record_event(self, incident_id: str, event_name: str, details: str):
        if incident_id not in self._timeline:
            self._timeline[incident_id] = []
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_name,
            "details": details
        }
        self._timeline[incident_id].append(entry)
        print(f"[HealingTimeline] {incident_id}: {event_name}")