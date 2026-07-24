"""
Enterprise Dependency Analyzer.
Orchestrates the pure DependencyEngine and formats findings.
"""
from typing import Dict, Any, Union
import time
from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.base.analyzer_models import (
    AnalyzerContext, AnalyzerMetadata, AnalyzerResult, AnalyzerCategory, AnalyzerPriority, 
    CloudProvider, SupportedResource, ExecutionMode, AnalyzerFinding, Severity, FindingStatus
)

# Core Platform Engines
from app.services.ai.analyzers.engines.graph.adapters.graph_adapter import GraphAdapter
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.graph.traversal_service import TraversalService
from app.services.ai.analyzers.engines.dependency.dependency_engine import DependencyEngine
from app.services.ai.analyzers.engines.dependency.root_cause_engine import RootCauseEngine
from app.services.ai.analyzers.engines.dependency.recommendation_engine import RecommendationEngine
from app.services.ai.analyzers.engines.dependency.failure_simulation_engine import FailureSimulationEngine
from app.services.ai.analyzers.engines.dependency.knowledge_graph_engine import KnowledgeGraphEngine
from app.services.ai.analyzers.engines.dependency.enterprise_reporting import EnterpriseReportingService
from app.services.ai.analyzers.engines.scoring.scoring_engine import ScoringEngine


class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes resource dependencies and blast radius using the Infrastructure Graph Engine."""

    @property
    def metadata(self) -> AnalyzerMetadata:
        return AnalyzerMetadata(
            id="dependency_analyzer",
            name="Dependency Analyzer",
            version="2.0.0",
            description="Analyzes downstream and upstream resource dependencies deterministically.",
            category=AnalyzerCategory.DEPENDENCY,
            priority=AnalyzerPriority.P1,
            execution_mode=ExecutionMode.SYNC,
            provider=CloudProvider.MULTI_CLOUD,
            supported_clouds=[CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE],
            supported_resources=[SupportedResource.ALL],
        )

    def validate(self, context: Union[AnalyzerContext, Dict[str, Any]]) -> bool:
        ctx = self._coerce_context(context)
        # Ensure we actually have raw graph payload
        return bool(ctx.graph)

    def analyze(self, context: Union[AnalyzerContext, Dict[str, Any]]) -> AnalyzerResult:
        start_time = time.time()
        ctx = self._coerce_context(context)
        infra_graph = GraphAdapter.fetch_graph(ctx.graph)
        
        # 1. Build Index (O(V+E))
        graph_index = GraphIndex.build(infra_graph)
        
        # 2. Knowledge Graph Enrichment
        kg_enrichment = KnowledgeGraphEngine.enrich(infra_graph, graph_index)
        
        # 3. Precompute expensive global structures
        # Pre-compute cycles globally (O(V+E)) to prevent O(V^2) operations
        all_sccs = TraversalService.tarjan_scc(graph_index)
        node_to_cycle = {}
        for scc in all_sccs:
            if len(scc) > 1:
                for n in scc:
                    node_to_cycle[n] = scc
                    
        all_findings = []
        all_recommendations = []
        
        # 4. Analyze every node deterministically using pure Domain engines
        for node_id in infra_graph.nodes.keys():
            cycle_for_node = node_to_cycle.get(node_id)
            # Run Dependency Engine
            analysis = DependencyEngine.analyze(infra_graph, graph_index, node_id, cycle=cycle_for_node)
            
            # Use Scoring Engine universally
            risk = ScoringEngine.calculate_risk(analysis.blast_radius, analysis.is_spof, analysis.is_isolated)
            
            # If there's high risk or a SPOF, generate an Enterprise Finding
            if risk.numeric_score >= 30.0:
                rc_analysis = RootCauseEngine.analyze(infra_graph, graph_index, node_id, analysis)
                simulation = FailureSimulationEngine.simulate(infra_graph, graph_index, node_id)
                recs = RecommendationEngine.generate(analysis)
                all_recommendations.extend(recs)
                
                # Map concrete resource type to abstract SupportedResource
                mapping = {
                    "S3Bucket": SupportedResource.STORAGE,
                    "EBS": SupportedResource.STORAGE,
                    "EC2": SupportedResource.COMPUTE,
                    "Lambda": SupportedResource.COMPUTE,
                    "SecurityGroup": SupportedResource.NETWORK,
                    "VPC": SupportedResource.NETWORK,
                    "Subnet": SupportedResource.NETWORK,
                    "RouteTable": SupportedResource.NETWORK,
                    "NACL": SupportedResource.NETWORK,
                    "InternetGateway": SupportedResource.NETWORK,
                    "NATGateway": SupportedResource.NETWORK,
                    "RDS": SupportedResource.DATABASE,
                    "DynamoDB": SupportedResource.DATABASE,
                    "IAMPolicy": SupportedResource.IAM,
                    "IAMRole": SupportedResource.IAM,
                    "IAMUser": SupportedResource.IAM,
                }
                abstract_type = mapping.get(analysis.node_type, SupportedResource.ALL)
                
                finding = AnalyzerFinding(
                    id=f"DEP-{node_id}",
                    title=f"High Risk Dependency: {analysis.node_type}",
                    description=risk.reason,
                    resource_id=node_id,
                    resource_type=abstract_type,
                    severity=Severity(risk.level.name),
                    status=FindingStatus.OPEN,
                    risk_level=risk.level,
                    business_impact=f"Criticality: {analysis.business_criticality}. {simulation.business_impact}",
                    technical_impact=f"Root Causes: {'; '.join(rc_analysis['likely_causes'])}. Service Impact: {', '.join(simulation.service_impact)}",
                    metadata={"dependency_analysis": analysis}
                )
                all_findings.append(finding)
                
        # 5. Compile Telemetry
        execution_time_ms = int((time.time() - start_time) * 1000)
        telemetry = {
            "execution_time_ms": execution_time_ms,
            "nodes_analyzed": len(infra_graph.nodes),
            "edges_analyzed": len(infra_graph.edges),
            "knowledge_graph": kg_enrichment
        }
        
        # 6. Generate Enterprise Report
        raw_analyses = [f.metadata.get("dependency_analysis") for f in all_findings if "dependency_analysis" in f.metadata]
        if raw_analyses:
            report = EnterpriseReportingService.generate_report(raw_analyses, telemetry)
        else:
            report = {}
                
        return AnalyzerResult(
            analyzer_id=self.metadata.id,
            score=self.calculate_score(AnalyzerResult(analyzer_id=self.metadata.id, findings=all_findings)),
            summary=f"Analyzed {len(infra_graph.nodes)} nodes. Found {len(all_findings)} high-risk dependencies.",
            findings=all_findings,
            recommendations=all_recommendations,
            execution_time_ms=execution_time_ms,
            resources_examined=len(infra_graph.nodes),
            metadata={"enterprise_report": report},
            telemetry=telemetry
        )

    def calculate_score(self, result: AnalyzerResult) -> int:
        return super().calculate_score(result)
