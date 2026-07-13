from typing import List
from app.services.ai.assistant.execution_plan import ToolResult
from app.services.ai.assistant.reasoning.reasoning_models import ReasoningResult
from app.services.ai.assistant.reasoning.evidence_ranker import EvidenceRanker
from app.services.ai.assistant.reasoning.risk_prioritizer import RiskPrioritizer
from app.services.ai.assistant.reasoning.conflict_resolver import ConflictResolver
from app.services.ai.assistant.reasoning.reasoning_validator import ReasoningValidator
from app.services.ai.assistant.reasoning.reasoning_explainer import ReasoningExplainer

class ReasoningEngine:
    def __init__(self):
        self.evidence_ranker = EvidenceRanker()
        self.conflict_resolver = ConflictResolver()
        self.risk_prioritizer = RiskPrioritizer()
        self.validator = ReasoningValidator()
        self.explainer = ReasoningExplainer()

    def process(self, session_id: str, tool_results: List[ToolResult]) -> ReasoningResult:
        """
        Orchestrates the reasoning components to convert ToolResults into a ReasoningResult.
        """
        # 1. Rank Evidence & Extract Findings
        findings, evidence = self.evidence_ranker.rank_evidence(tool_results)
        
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