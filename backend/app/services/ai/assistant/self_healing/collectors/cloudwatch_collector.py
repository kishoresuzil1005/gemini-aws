from typing import Dict, Any
from ..detection.incident_detector import IncidentDetector

class CloudWatchCollector:
    """
    Ingests and normalizes alerts specific to AWS CloudWatch.
    """
    def __init__(self, detector: IncidentDetector):
        self.detector = detector

    def process_sns_payload(self, sns_message: Dict[str, Any]):
        print("[CloudWatchCollector] Parsing SNS payload from CloudWatch...")
        # Translate CloudWatch format to unified format
        normalized = {
            "instance_id": sns_message.get("Trigger", {}).get("Dimensions", [{}])[0].get("value"),
            "severity": "HIGH",
            "source": "aws.cloudwatch",
            "metric": sns_message.get("Trigger", {}).get("MetricName")
        }
        return self.detector.ingest_alert(normalized)
