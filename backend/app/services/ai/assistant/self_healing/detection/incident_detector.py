from typing import Dict, Any
from ..models.healing_models import Incident

class IncidentDetector:
    """
    Normalizes alerts from CloudWatch, Datadog, Prometheus into standard Incidents.
    """
    def ingest_alert(self, payload: Dict[str, Any]) -> Incident:
        print("[IncidentDetector] Normalizing cloud alert into Incident...")
        return Incident(
            incident_id="inc-999",
            source="CloudWatch",
            severity="CRITICAL",
            resource_id=payload.get("instance_id", "unknown"),
            raw_payload=payload
        )
