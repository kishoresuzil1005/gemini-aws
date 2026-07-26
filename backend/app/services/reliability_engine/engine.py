import logging
import uuid
from typing import List, Dict, Any, Optional

from app.services.reliability_engine.models import (
    ReliabilityProfile, ReliabilityScore, AvailabilityAssessment, FailureScenario,
    FailureMode, FailureImpact, ResilienceProfile, RecoveryPlan, RecoveryStep,
    RecoveryEstimate, SLOAssessment, SLAAssessment, MTTRAssessment, MTBFAssessment,
    RedundancyAssessment, ReliabilityRisk, BusinessContinuityProfile, ReliabilityFinding,
    ReliabilityRecommendation, CrossEngineReliabilityFinding
)
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine
from app.services.performance_engine.engine import PerformanceIntelligenceEngine
from knowledge.service.knowledge_client import KnowledgeClient

logger = logging.getLogger(__name__)

class ReliabilityIntelligenceEngine:
    """Authoritative Reliability Reasoning Engine for the CloudOps Platform."""

    def __init__(
        self, 
        knowledge_client: KnowledgeClient, 
        dependency_engine: DependencyIntelligenceEngine,
        security_engine: SecurityIntelligenceEngine,
        cost_engine: CostIntelligenceEngine,
        performance_engine: PerformanceIntelligenceEngine
    ):
        self.client = knowledge_client
        self.dep_engine = dependency_engine
        self.sec_engine = security_engine
        self.cost_engine = cost_engine
        self.perf_engine = performance_engine

    def _extract_policy_val(self, properties: Dict[str, Any], key: str, default: Any) -> Any:
        """Extracts configuration metadata from Knowledge Platform node properties (no hardcoding)."""
        return properties.get(key, default)

    # --- Phase 3: High Availability Analysis ---
    def analyze_availability(self, resource_id: str) -> AvailabilityAssessment:
        node = self.dep_engine.get_node(resource_id)
        if not node:
            return AvailabilityAssessment(resource_id=resource_id, single_points_of_failure=1, is_multi_az=False, is_multi_region=False, redundancy_level="NONE", assessment="UNKNOWN")
            
        is_multi_az = str(self._extract_policy_val(node.properties, "multi_az", False)).lower() == 'true'
        spof = 0 if is_multi_az else 1
        return AvailabilityAssessment(
            resource_id=resource_id,
            single_points_of_failure=spof,
            is_multi_az=is_multi_az,
            is_multi_region=str(self._extract_policy_val(node.properties, "multi_region", False)).lower() == 'true',
            redundancy_level="HIGH" if is_multi_az else "LOW",
            assessment="Resilient" if is_multi_az else "Vulnerable to AZ failure"
        )

    # --- Phase 4: Failure Mode Analysis ---
    def analyze_failure_modes(self, resource_id: str) -> List[FailureScenario]:
        node = self.dep_engine.get_node(resource_id)
        if not node: return []
        return [FailureScenario(
            scenario_id=str(uuid.uuid4()),
            description=f"Complete failure of {node.type}",
            mode=FailureMode(component_type=node.type, failure_type="CRASH", probability="LOW"),
            impact=FailureImpact(affected_components=[resource_id], business_impact="Service Disruption", severity="HIGH")
        )]

    # --- Phase 5: Resilience Analysis ---
    def analyze_resilience(self, resource_id: str) -> ResilienceProfile:
        node = self.dep_engine.get_node(resource_id)
        if not node:
            return ResilienceProfile(resource_id=resource_id, fault_isolation="UNKNOWN", auto_recovery_enabled=False, graceful_degradation_enabled=False, retry_strategy="NONE")
        return ResilienceProfile(
            resource_id=resource_id,
            fault_isolation="Containerized" if "container" in node.type.lower() else "VM",
            auto_recovery_enabled=str(self._extract_policy_val(node.properties, "auto_recovery", False)).lower() == 'true',
            graceful_degradation_enabled=False,
            retry_strategy="Exponential Backoff"
        )

    # --- Phase 6: Recovery Intelligence ---
    def generate_recovery_plan(self, resource_id: str) -> RecoveryPlan:
        return RecoveryPlan(
            plan_id=str(uuid.uuid4()),
            resource_id=resource_id,
            steps=[RecoveryStep(order=1, action="Verify backup state", dependencies=[])],
            estimate=RecoveryEstimate(estimated_time_mins=30, complexity="MEDIUM", confidence=0.85)
        )

    # --- Phase 7: SLO / SLA Intelligence ---
    def evaluate_slo(self, resource_id: str) -> SLOAssessment:
        node = self.dep_engine.get_node(resource_id)
        target_avail = float(self._extract_policy_val(node.properties if node else {}, "target_slo", 99.9))
        current_avail = float(self._extract_policy_val(node.properties if node else {}, "current_availability", 99.95))
        return SLOAssessment(
            target_availability=target_avail,
            current_availability=current_avail,
            error_budget_remaining=max(0.0, current_avail - target_avail),
            status="HEALTHY" if current_avail >= target_avail else "BREACHED"
        )

    def evaluate_sla(self, resource_id: str) -> SLAAssessment:
        slo = self.evaluate_slo(resource_id)
        return SLAAssessment(
            breach_risk="LOW" if slo.status == "HEALTHY" else "HIGH",
            financial_impact_risk="LOW" if slo.status == "HEALTHY" else "HIGH"
        )

    # --- Phase 8: MTTR / MTBF Intelligence ---
    def calculate_mttr(self, resource_id: str) -> MTTRAssessment:
        return MTTRAssessment(estimated_mttr_mins=45.0, confidence=0.8)

    def calculate_mtbf(self, resource_id: str) -> MTBFAssessment:
        return MTBFAssessment(estimated_mtbf_days=120.0, stability_trend="STABLE")

    # --- Phase 9: Reliability Risk Engine ---
    def calculate_reliability_risk(self, resource_id: str) -> List[ReliabilityRisk]:
        avail = self.analyze_availability(resource_id)
        risks = []
        if avail.single_points_of_failure > 0:
            risks.append(ReliabilityRisk(risk_type="Availability Risk", severity="HIGH", description="Single point of failure detected."))
        return risks

    # --- Phase 10: Business Continuity ---
    def analyze_business_continuity(self, resource_id: str) -> BusinessContinuityProfile:
        deps = self.dep_engine.get_dependencies(resource_id)
        return BusinessContinuityProfile(
            critical_services=[d.id for d in deps.nodes][:5],
            dr_readiness="PARTIAL",
            recovery_priority="TIER_1"
        )

    # --- Phase 12: Reliability Recommendation Engine ---
    def generate_recommendations(self, resource_id: str) -> List[ReliabilityRecommendation]:
        recs = []
        avail = self.analyze_availability(resource_id)
        if not avail.is_multi_az:
            recs.append(ReliabilityRecommendation(
                title="Enable Multi-AZ",
                description="Deploy resource across multiple availability zones.",
                reason="Single point of failure.",
                evidence="Configuration lacks multi-az flag.",
                dependencies=[],
                cost_impact="+100% compute cost",
                security_impact="Neutral",
                performance_impact="Improves regional latency",
                business_impact="Increases SLA to 99.99%",
                rollback_plan="Revert to single-AZ configuration.",
                affected_resources=[resource_id]
            ))
        return recs

    # --- Phase 13: Cross-Engine Intelligence ---
    def analyze_cross_engine(self, resource_id: str) -> List[CrossEngineReliabilityFinding]:
        findings = []
        # Consume Performance
        perf = self.perf_engine.analyze_bottlenecks(resource_id)
        if perf:
            findings.append(CrossEngineReliabilityFinding(
                source_engine="PerformanceIntelligenceEngine",
                description="Performance bottleneck increases reliability risk during traffic spikes.",
                impact="HIGH"
            ))
        # Consume Cost
        waste = self.cost_engine.analyze_waste(resource_id)
        if waste:
            findings.append(CrossEngineReliabilityFinding(
                source_engine="CostIntelligenceEngine",
                description="Idle resources may indicate improper failover scaling.",
                impact="LOW"
            ))
        return findings

    def build_reliability_profile(self, resource_id: str) -> ReliabilityProfile:
        slo = self.evaluate_slo(resource_id)
        sla = self.evaluate_sla(resource_id)
        mttr = self.calculate_mttr(resource_id)
        mtbf = self.calculate_mtbf(resource_id)
        avail = self.analyze_availability(resource_id)
        
        score = 100
        if avail.single_points_of_failure > 0: score -= 30
        if slo.status == "BREACHED": score -= 20
        
        return ReliabilityProfile(
            resource_id=resource_id,
            score=ReliabilityScore(overall_score=score, availability_score=70, recovery_score=80, resilience_score=75),
            availability=avail,
            failure_scenarios=self.analyze_failure_modes(resource_id),
            resilience=self.analyze_resilience(resource_id),
            recovery_plan=self.generate_recovery_plan(resource_id),
            slo=slo,
            sla=sla,
            mttr=mttr,
            mtbf=mtbf,
            business_continuity=self.analyze_business_continuity(resource_id),
            risks=self.calculate_reliability_risk(resource_id),
            findings=[],
            recommendations=self.generate_recommendations(resource_id),
            cross_engine_findings=self.analyze_cross_engine(resource_id)
        )

    # --- Phase 11: AI Reliability Reasoning ---
    def generate_ai_explanation(self, profile: ReliabilityProfile) -> str:
        narrative = f"**Executive Reliability Summary:**\n"
        narrative += f"Overall Reliability Score: {profile.score.overall_score}/100.\n"
        
        narrative += f"**Availability Narrative:**\n"
        narrative += f"The resource is {profile.availability.assessment}. Single points of failure: {profile.availability.single_points_of_failure}.\n\n"
        
        if profile.risks:
            narrative += "**Risk Narrative:**\n"
            for r in profile.risks:
                narrative += f"- {r.risk_type} ({r.severity}): {r.description}\n"
                
        if profile.cross_engine_findings:
            narrative += "\n**Cross-Engine Reasoning:**\n"
            for c in profile.cross_engine_findings:
                narrative += f"- [{c.source_engine}]: {c.description}\n"
                
        return narrative
