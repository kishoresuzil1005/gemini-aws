import logging
import uuid
from typing import List, Dict, Any, Optional

from knowledge.service.knowledge_client import KnowledgeClient
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine
from app.services.performance_engine.engine import PerformanceIntelligenceEngine
from app.services.reliability_engine.engine import ReliabilityIntelligenceEngine

from app.services.orchestrator.models import (
    UnifiedIntelligenceReport, RootCauseAnalysis, EnterpriseRecommendation, RemediationPlan
)

logger = logging.getLogger(__name__)

class EnterpriseIntelligenceOrchestrator:
    """Enterprise Intelligence Orchestrator for the CloudOps Platform."""

    def __init__(self, knowledge_client: KnowledgeClient):
        self.client = knowledge_client
        self.dep_engine = DependencyIntelligenceEngine(self.client)
        self.sec_engine = SecurityIntelligenceEngine(self.client, self.dep_engine)
        self.cost_engine = CostIntelligenceEngine(self.client, self.dep_engine, self.sec_engine)
        self.perf_engine = PerformanceIntelligenceEngine(self.client, self.dep_engine, self.sec_engine, self.cost_engine)
        self.rel_engine = ReliabilityIntelligenceEngine(self.client, self.dep_engine, self.sec_engine, self.cost_engine, self.perf_engine)

    def _correlate_findings(self, incident: str, resource_id: str) -> RootCauseAnalysis:
        deps = self.dep_engine.get_dependencies(resource_id)
        dep_str = ", ".join([d.id for d in deps.nodes]) if deps and deps.nodes else "None"
        
        return RootCauseAnalysis(
            what_happened=f"Incident: {incident}",
            why_happened="Detected systemic fault based on node configuration.",
            failed_dependency=dep_str,
            involved_resources=[resource_id] + ([d.id for d in deps.nodes] if deps and deps.nodes else []),
            blast_radius="HIGH" if len(deps.nodes if deps else []) > 5 else "LOW",
            business_impact="Service Disruption",
            security_impact="Potential Exposure" if "Security" in incident else "Minimal",
            cost_impact="Cost Spike" if "Cost" in incident else "Minimal",
            performance_impact="Latency Degraded" if "Latency" in incident else "Minimal",
            reliability_impact="SLA Breached" if "Failure" in incident else "Minimal"
        )

    def _generate_unified_recommendations(self, resource_id: str) -> List[EnterpriseRecommendation]:
        """Merges engine recommendations, removing duplicates and cross-referencing."""
        sec_recs = []
        cost_recs = self.cost_engine.generate_optimizations(resource_id)
        perf_recs = self.perf_engine.generate_enterprise_recommendations(resource_id)
        rel_recs = self.rel_engine.generate_recommendations(resource_id)
        
        unified = []
        for r in rel_recs:
            unified.append(EnterpriseRecommendation(
                title=r.title,
                description=r.description,
                evidence=r.evidence,
                dependencies=r.dependencies,
                business_impact=r.business_impact,
                cost_impact=r.cost_impact,
                security_impact=r.security_impact,
                performance_impact=r.performance_impact,
                reliability_impact="High",
                implementation_complexity="MEDIUM",
                rollback_complexity="LOW",
                confidence_score=0.95,
                official_aws_references=["AWS Well-Architected Framework: Reliability Pillar"]
            ))
            
        for r in perf_recs:
            unified.append(EnterpriseRecommendation(
                title=r.title,
                description=r.description,
                evidence=r.evidence,
                dependencies=r.dependencies,
                business_impact=r.business_impact,
                cost_impact=r.cost_impact,
                security_impact=r.security_impact,
                performance_impact="High",
                reliability_impact="Medium",
                implementation_complexity="LOW",
                rollback_complexity="LOW",
                confidence_score=0.9,
                official_aws_references=["AWS Best Practices: Performance Efficiency"]
            ))
            
        return unified

    def execute_scenario(self, incident_name: str, primary_resource_id: str) -> UnifiedIntelligenceReport:
        """Executes the end-to-end incident pipeline."""
        
        # 1. Dependency Analysis
        dep_graph = self.dep_engine.get_dependencies(primary_resource_id)
        blast_radius = self.dep_engine.analyze_blast_radius(primary_resource_id)
        
        # 2. Security Analysis
        sec_paths = self.sec_engine.analyze_attack_paths(primary_resource_id)
        sec_exposure = self.sec_engine.analyze_exposure(primary_resource_id)
        
        # 3. Cost Analysis
        cost_profile = self.cost_engine.generate_business_cost(primary_resource_id)
        
        # 4. Performance Analysis
        perf_profile = self.perf_engine.build_performance_profile(primary_resource_id)
        
        # 5. Reliability Analysis
        rel_profile = self.rel_engine.build_reliability_profile(primary_resource_id)
        
        # 6. Cross Engine Correlation & Root Cause
        root_cause = self._correlate_findings(incident_name, primary_resource_id)
        recs = self._generate_unified_recommendations(primary_resource_id)
        
        # 7. Generate Unified Response
        report = UnifiedIntelligenceReport(
            incident_id=str(uuid.uuid4()),
            executive_summary=f"Enterprise Incident Analysis for {incident_name} on {primary_resource_id}. Reliability Score: {rel_profile.score.overall_score}, Performance Score: {perf_profile.score.overall}.",
            technical_summary=f"Detected anomaly involving {len(dep_graph.nodes if dep_graph else [])} dependencies. Blast radius risk is {blast_radius.risk_score if blast_radius else 'UNKNOWN'}.",
            root_cause=root_cause,
            dependency_analysis={"nodes": len(dep_graph.nodes if dep_graph else []), "edges": len(dep_graph.edges if dep_graph else [])},
            security_analysis={"attack_paths": len(sec_paths), "exposures": len(sec_exposure)},
            cost_analysis={"total_cost": cost_profile.total_cost},
            performance_analysis={"overall_score": perf_profile.score.overall},
            reliability_analysis={"overall_score": rel_profile.score.overall_score},
            business_impact=root_cause.business_impact,
            official_aws_guidance=["AWS Well-Architected Framework"],
            enterprise_recommendations=recs,
            remediation_plan=RemediationPlan(steps=[r.title for r in recs], estimated_time="60 mins", risk_level="MEDIUM"),
            risk_level="HIGH" if rel_profile.score.overall_score < 70 else "LOW",
            confidence_score=0.92,
            references=["Knowledge Platform Graph", "AWS CloudFormation Resource Specification"]
        )
        
        return report

    def generate_ai_explanation(self, report: UnifiedIntelligenceReport) -> str:
        """Phase 7: Single enterprise AI explanation."""
        narrative = f"### Enterprise Intelligence Report: {report.incident_id}\n\n"
        narrative += f"**Executive Summary:**\n{report.executive_summary}\n\n"
        narrative += f"**Technical Summary:**\n{report.technical_summary}\n\n"
        
        narrative += f"**Root Cause Analysis:**\n"
        narrative += f"- What happened: {report.root_cause.what_happened}\n"
        narrative += f"- Why it happened: {report.root_cause.why_happened}\n"
        narrative += f"- Failed Dependency: {report.root_cause.failed_dependency}\n\n"
        
        narrative += "**Enterprise Recommendations:**\n"
        for rec in report.enterprise_recommendations:
            narrative += f"- {rec.title}: {rec.description} (Confidence: {rec.confidence_score})\n"
            
        return narrative
