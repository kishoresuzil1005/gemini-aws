"""
Investigation Session — Phase 2
=================================
Holds the full state of a multi-turn infrastructure investigation.
Persisted to Redis with a 30-minute TTL.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class InvestigationStatus(str, Enum):
    OPEN        = "open"
    RUNNING     = "running"
    PENDING_APPROVAL = "pending_approval"
    RESOLVED    = "resolved"
    FAILED      = "failed"
    CLOSED      = "closed"


@dataclass
class Evidence:
    source: str           # provider name
    data: Dict[str, Any]
    collected_at: float = field(default_factory=time.time)
    confidence: float = 1.0


@dataclass
class TimelineEvent:
    event_type: str       # user_question | provider_result | llm_response | system
    summary: str
    detail: Dict[str, Any] = field(default_factory=dict)
    ts: float = field(default_factory=time.time)


@dataclass
class InvestigationSession:
    """
    Full state machine for one investigation.
    Created when the user asks a question; updated as providers return data.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    status: InvestigationStatus = InvestigationStatus.OPEN
    root_symptom: str = ""
    root_resource_id: Optional[str] = None
    intent: str = "general"

    # Evidence collected from providers
    evidence: List[Evidence] = field(default_factory=list)

    # Dependency graph edges: {resource_id: [related_resource_ids]}
    dependency_graph: Dict[str, List[str]] = field(default_factory=dict)

    # Ordered timeline of events
    timeline: List[TimelineEvent] = field(default_factory=list)

    # Recommendations generated
    recommendations: List[str] = field(default_factory=list)

    # Remediation plan (if any)
    remediation_plan: Optional[Dict[str, Any]] = None

    # Timestamps
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None

    # ------------------------------------------------------------------
    def add_evidence(self, source: str, data: Dict[str, Any], confidence: float = 1.0) -> None:
        self.evidence.append(Evidence(source=source, data=data, confidence=confidence))
        self.updated_at = time.time()

    def add_timeline(self, event_type: str, summary: str, detail: Optional[Dict] = None) -> None:
        self.timeline.append(TimelineEvent(event_type=event_type, summary=summary, detail=detail or {}))
        self.updated_at = time.time()

    def add_dependency(self, source_id: str, target_id: str) -> None:
        self.dependency_graph.setdefault(source_id, [])
        if target_id not in self.dependency_graph[source_id]:
            self.dependency_graph[source_id].append(target_id)
        self.updated_at = time.time()

    def transition(self, new_status: InvestigationStatus) -> None:
        self.status = new_status
        self.updated_at = time.time()
        if new_status == InvestigationStatus.RESOLVED:
            self.resolved_at = time.time()

    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvestigationSession":
        data = dict(data)
        data["status"] = InvestigationStatus(data.get("status", "open"))
        evidence_raw = data.pop("evidence", [])
        timeline_raw = data.pop("timeline", [])
        session = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        session.evidence = [Evidence(**e) for e in evidence_raw]
        session.timeline = [TimelineEvent(**t) for t in timeline_raw]
        return session

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, raw: str) -> "InvestigationSession":
        return cls.from_dict(json.loads(raw))
