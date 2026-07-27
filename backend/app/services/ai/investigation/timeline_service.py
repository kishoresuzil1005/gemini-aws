"""Timeline Service — Phase 2"""
from __future__ import annotations
from typing import List
from .session import InvestigationSession, TimelineEvent


class TimelineService:
    def get_formatted(self, session: InvestigationSession) -> List[dict]:
        return [
            {"ts": e.ts, "type": e.event_type, "summary": e.summary, "detail": e.detail}
            for e in session.timeline
        ]
