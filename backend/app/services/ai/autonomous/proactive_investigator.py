"""Proactive Investigator — Phase 6"""
from __future__ import annotations
import logging
from typing import Any, Dict
from app.services.ai.investigation.session import InvestigationSession, InvestigationStatus
from .event_bus import EventBus

logger = logging.getLogger(__name__)


class ProactiveInvestigator:
    """
    Triggered by events (alarms, GuardDuty, etc.) to start autonomous
    investigations without waiting for a user question.
    """

    def __init__(self):
        EventBus.subscribe("alarm.triggered", self.on_alarm)

    async def on_alarm(self, payload: Dict[str, Any]) -> None:
        resource_id = payload.get("resource_id", "")
        alarm_name = payload.get("alarm_name", "")
        logger.info("[ProactiveInvestigator] Starting investigation for alarm: %s resource=%s",
                    alarm_name, resource_id)
        session = InvestigationSession(
            root_symptom=f"CloudWatch alarm: {alarm_name}",
            root_resource_id=resource_id,
            intent="health_check",
        )
        session.transition(InvestigationStatus.RUNNING)
        session.add_timeline("system", f"Proactive investigation started for alarm: {alarm_name}")
        logger.info("[ProactiveInvestigator] Session %s created", session.id)
        return session
