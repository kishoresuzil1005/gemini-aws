import uuid
from typing import Any, List
from app.services.ai.context_engine.models import AIContext
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult
from app.services.ai.assistant.reasoning.reasoning_models import Evidence, Finding
from app.services.ai.assistant.reasoning.risk_prioritizer import RiskPrioritizer
from app.services.ai.assistant.reasoning.conflict_resolver import ConflictResolver
from app.services.ai.assistant.reasoning.reasoning_validator import ReasoningValidator
from app.services.ai.assistant.reasoning.reasoning_explainer import ReasoningExplainer

class ReasoningEngine:
    def __init__(self):
        self.conflict_resolver = ConflictResolver()
        self.risk_prioritizer = RiskPrioritizer()
        self.validator = ReasoningValidator()
        self.explainer = ReasoningExplainer()

    def process(self, session_id: str, context: AIContext) -> ReasoningResult:
        """
        Interprets deterministic analysis stored in ``AIContext``.
        """
        # 1. Interpret deterministic analyzer output.  Reasoning never fetches
        # cloud data and no longer depends on assistant tools or execution plans.
        findings, evidence = self._extract_evidence(context)
        
        # 2. Resolve Conflicts
        conflicts = self.conflict_resolver.resolve_conflicts(findings)
        
        # 3. Prioritize Risks
        risks = self.risk_prioritizer.prioritize(findings)
        
        # 4. Validate Reasoning Quality
        is_valid, errors = self.validator.validate(findings, evidence, risks, conflicts)
        
        # 5. Generate Explanation
        explanation = self.explainer.explain(findings, evidence, risks, conflicts)
        
        return ReasoningResult(
            session_id=session_id,
            is_valid=is_valid,
            validation_errors=errors,
            findings=findings,
            evidence=evidence,
            risks=risks,
            conflicts=conflicts,
            explanation=explanation
        )

    @staticmethod
    def _extract_evidence(context: AIContext) -> tuple[List[Finding], List[Evidence]]:
        findings: List[Finding] = []
        evidence: List[Evidence] = []
        for analyzer_name, result in context.findings.items():
            for item in result.get("findings", []):
                finding_id = str(uuid.uuid4())
                description = item.get("description", f"Finding from {analyzer_name}")
                findings.append(Finding(
                    id=finding_id,
                    source_tool=analyzer_name,
                    description=description,
                    raw_data=item,
                ))
                evidence.append(Evidence(
                    id=str(uuid.uuid4()),
                    finding_id=finding_id,
                    description=description,
                    confidence=1.0,
                ))
        return findings, evidence
