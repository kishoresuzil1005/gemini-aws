import uuid
from typing import List
from app.services.ai.assistant.execution_plan import ToolResult
from app.services.ai.assistant.reasoning.reasoning_models import Evidence, Finding
from app.services.ai.assistant.reasoning.reasoning_rules import ReasoningRules

class EvidenceRanker:
    def rank_evidence(self, tool_results: List[ToolResult]) -> tuple[List[Finding], List[Evidence]]:
        """
        Extracts findings from tool results and converts them to Evidence,
        ranked by confidence.
        """
        findings: List[Finding] = []
        evidence_list: List[Evidence] = []
        
        for tr in tool_results:
            if not tr.context:
                continue
                
            # Simplistic extraction for Phase 4
            finding_id = str(uuid.uuid4())
            finding = Finding(
                id=finding_id,
                source_tool=tr.tool_name,
                description=f"Findings extracted from {tr.tool_name}",
                raw_data=tr.context
            )
            findings.append(finding)
            
            confidence = ReasoningRules.get_evidence_confidence(tr.tool_name)
            evidence = Evidence(
                id=str(uuid.uuid4()),
                finding_id=finding_id,
                description=f"Evidence from {tr.tool_name}",
                confidence=confidence
            )
            evidence_list.append(evidence)
            
        # Sort evidence descending by confidence, keep top 8
        evidence_list.sort(key=lambda e: e.confidence, reverse=True)
        top_evidence = evidence_list[:8]
        
        # Keep only findings related to the top 8 evidence
        top_finding_ids = {e.finding_id for e in top_evidence}
        top_findings = [f for f in findings if f.id in top_finding_ids]
        
        return top_findings, top_evidence
