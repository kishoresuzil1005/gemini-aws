"""
Context Validator (Phase 9)
============================
Validates that a UnifiedContext has all required sections before the
prompt is built. Returns structured errors instead of calling the LLM
with incomplete data.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List

from .models import UnifiedContext

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    valid: bool = True
    missing_sections: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "missing_sections": self.missing_sections,
            "warnings": self.warnings,
        }


class ContextValidator:
    """
    Validates context completeness.

    Required sections vary by intent:
      - health_check  → resource + metrics
      - security_audit → resource + findings
      - cost_analysis  → resource + cost
      - default        → resource
    """

    REQUIRED_BY_INTENT: dict = {
        "health_check": ["resource", "metrics"],
        "security_audit": ["resource", "findings"],
        "cost_analysis": ["resource", "cost"],
        "performance": ["resource", "metrics"],
        "relationship_query": ["resource", "relationships"],
    }

    def validate(self, ctx: UnifiedContext, intent: str = "general") -> ValidationReport:
        report = ValidationReport()
        required = self.REQUIRED_BY_INTENT.get(intent, ["resource"])

        if "resource" in required and ctx.resource is None:
            report.valid = False
            report.missing_sections.append("resource")

        if ctx.resource:
            if "metrics" in required and not ctx.resource.metrics:
                report.valid = False
                report.missing_sections.append("metrics")

            if "findings" in required and not ctx.resource.findings:
                report.warnings.append(
                    "No security findings returned — resource may be clean or provider unavailable."
                )

            if "cost" in required and ctx.resource.cost is None:
                report.warnings.append(
                    "Cost data unavailable — cost provider may have timed out."
                )

            if "relationships" in required and not ctx.resource.relationships:
                report.warnings.append(
                    "No relationship data — graph provider may be empty for this resource."
                )

        if ctx.has_errors():
            report.warnings.extend(ctx.errors)

        if not ctx.is_sufficient():
            report.warnings.append(
                f"Context quality score {ctx.quality.score:.2f} is below threshold 0.75."
            )

        logger.info(
            "[Validator] intent=%s valid=%s missing=%s warnings=%d",
            intent,
            report.valid,
            report.missing_sections,
            len(report.warnings),
        )
        return report
