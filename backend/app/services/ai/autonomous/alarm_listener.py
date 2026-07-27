"""CloudWatch Alarm Listener — Phase 6"""
from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from .event_bus import EventBus

logger = logging.getLogger(__name__)


class AlarmListener:
    """
    Listens for CloudWatch alarms (via EventBridge / SQS) and
    publishes them to the EventBus for proactive investigation.
    """

    async def handle_alarm(self, alarm_payload: Dict[str, Any]) -> None:
        alarm_name = alarm_payload.get("AlarmName", "unknown")
        resource_id = alarm_payload.get("Trigger", {}).get("Dimensions", [{}])[0].get("value", "")
        logger.warning("[AlarmListener] Alarm triggered: %s resource=%s", alarm_name, resource_id)
        await EventBus.publish("alarm.triggered", {
            "alarm_name": alarm_name,
            "resource_id": resource_id,
            "payload": alarm_payload,
        })
