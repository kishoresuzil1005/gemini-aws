"""
O(N) Engine for generating Remediation Plans from Security Findings.
"""
import time
import uuid
from typing import List, Optional
from app.services.ai.analyzers.engines.security.security_models import SecurityFinding
from app.services.ai.analyzers.engines.remediation.remediation_models import (
    RemediationPlan, RemediationAction, RemediationStatus, RemediationComplexity,
    RemediationPriority, EstimatedDowntime, EstimatedDuration, MaintenanceWindow,
    RiskAssessment, ImpactAssessment, ApprovalRequirement, AutomationPlan,
    AutomationCapability, ExecutionMode, RemediationStep
)
from app.services.ai.analyzers.engines.remediation.remediation_registry import RemediationRegistry
from app.services.ai.analyzers.engines.remediation.remediation_validator import RemediationValidator

class RemediationEngine:
    """
    Stateless, thread-safe aggregator for Remediation generation.
    """
    def __init__(self, registry: RemediationRegistry = None):
        self.registry = registry or RemediationRegistry()
        self.validator = RemediationValidator()

    def _build_action(self, finding: SecurityFinding, format_name: str, step: RemediationStep) -> RemediationAction:
        return RemediationAction(
            action_id=f"act-{uuid.uuid4().hex[:8]}",
            title=f"Remediate via {format_name}",
            description=f"Generated {format_name} plan for {finding.rule_id}",
            complexity=RemediationComplexity.LOW,
            priority=RemediationPriority(finding.base_severity.value),
            downtime=EstimatedDowntime(minutes=0, is_disruptive=False),
            duration=EstimatedDuration(minutes=5, description="Expected execution time"),
            maintenance_window=MaintenanceWindow(required=False),
            risk=RiskAssessment(level=RemediationPriority(finding.base_severity.value), description="Low risk state change", data_loss_risk=False),
            impact=ImpactAssessment(technical_impact="Resolves finding", business_impact="Improves compliance"),
            approval=ApprovalRequirement(required=True, roles=["CloudAdmin"]),
            steps=[step],
            automation=AutomationPlan(
                capability=AutomationCapability(is_automatable=True, confidence=0.9, reason="Structured command available"),
                mode=ExecutionMode.SEMI_AUTOMATIC
            )
        )

    def generate_plan(self, finding: SecurityFinding) -> RemediationPlan:
        """
        Consumes a single finding and generates a multi-format RemediationPlan.
        """
        actions = []
        
        for fmt in self.registry.list_generators():
            generator = self.registry.find_generator(fmt)
            if generator:
                step = generator.generate(finding)
                if step and self.validator.validate_step(step):
                    actions.append(self._build_action(finding, fmt, step))
                    
        return RemediationPlan(
            plan_id=str(uuid.uuid4()),
            finding_id=finding.rule_id,
            resource_id=finding.resource_id,
            status=RemediationStatus.PENDING,
            actions=actions,
            generated_at=time.time()
        )

    def generate_plans_batch(self, findings: List[SecurityFinding]) -> List[RemediationPlan]:
        """
        O(N) batch processing.
        """
        return [self.generate_plan(f) for f in findings]
