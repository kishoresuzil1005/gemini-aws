"""
Planner Rule Set
=================
Maps (intent, service_hints) → required providers.
This is pure data — no I/O, no LLM, just a decision table.
"""

from __future__ import annotations
from typing import Dict, List, Set

# ---------------------------------------------------------------------------
# Intent → required providers
# ---------------------------------------------------------------------------

INTENT_PROVIDER_MAP: Dict[str, List[str]] = {
    "health_check":       ["inventory", "graph", "metrics", "security"],
    "security_audit":     ["inventory", "graph", "security"],
    "cost_analysis":      ["inventory", "cost"],
    "performance":        ["inventory", "metrics"],
    "relationship_query": ["inventory", "graph"],
    "remediation":        ["inventory", "graph", "security", "cost"],
    "general":            ["inventory", "graph"],
    "ROOT_CAUSE":         ["inventory", "graph", "metrics", "security"],
    "SECURITY":           ["inventory", "graph", "security"],
    "DEPENDENCY":         ["inventory", "graph"],
    "BLAST_RADIUS":       ["inventory", "graph"],
    "RECOMMENDATION":     ["inventory", "graph", "metrics", "cost", "security"],
    "REMEDIATION":        ["inventory", "graph", "security", "cost"],
    "ORCHESTRATION":      ["inventory", "graph"],
    "DOCUMENTATION":      ["documentation"],
    "INVENTORY":          ["inventory"],
    "UNKNOWN":            ["inventory", "graph"],
}

# If these services are mentioned, always add the corresponding provider
SERVICE_PROVIDER_MAP: Dict[str, List[str]] = {
    "ec2":          ["inventory", "metrics"],
    "rds":          ["inventory", "metrics", "cost"],
    "lambda":       ["inventory", "metrics"],
    "s3":           ["inventory", "cost", "security"],
    "iam":          ["inventory", "security"],
    "vpc":          ["inventory", "graph"],
    "cloudwatch":   ["metrics"],
    "guardduty":    ["security"],
    "inspector":    ["security"],
    "kms":          ["inventory", "security"],
    "cloudtrail":   ["inventory", "security"],
}


def required_providers(intent: str, service_hints: List[str] = None) -> List[str]:
    """Return the deduplicated ordered list of required providers."""
    service_hints = service_hints or []
    required: Set[str] = set(INTENT_PROVIDER_MAP.get(intent, ["inventory", "graph"]))
    for svc in service_hints:
        extra = SERVICE_PROVIDER_MAP.get(svc.lower(), [])
        required.update(extra)

    # Canonical ordering
    order = ["inventory", "graph", "metrics", "security", "cost", "documentation"]
    return [p for p in order if p in required] + [p for p in required if p not in order]
