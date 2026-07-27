"""Risk Scorer — Phase 4"""
from __future__ import annotations
from typing import Any, Dict


class RiskScorer:
    """Computes a risk score (0-100) for a proposed remediation action."""

    RISK_WEIGHTS = {
        "restart_instance":         20,
        "stop_instance":            35,
        "terminate_instance":       90,
        "modify_security_group":    60,
        "delete_security_group":    80,
        "apply_patch":              15,
        "change_iam_policy":        75,
        "scale_out":                10,
        "resize_instance":          30,
    }

    def score(self, action: str, context: Dict[str, Any]) -> int:
        base = self.RISK_WEIGHTS.get(action, 50)
        # Increase risk for production resources
        env = str(context.get("environment", "")).lower()
        if "prod" in env:
            base = min(100, int(base * 1.4))
        return base
