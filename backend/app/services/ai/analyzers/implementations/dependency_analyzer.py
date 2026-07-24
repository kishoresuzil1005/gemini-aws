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
from app.services.ai.analyzers.engines.graph.adapters.neo4j_adapter import Neo4jAdapter
from app.services.ai.analyzers.engines.graph.graph_index import GraphIndex
from app.services.ai.analyzers.engines.graph.traversal_service import TraversalService
from app.services.ai.analyzers.engines.dependency.dependency_engine import DependencyEngine
from app.services.ai.analyzers.engines.dependency.root_cause_engine import RootCauseEngine
from app.services.ai.analyzers.engines.dependency.recommendation_engine import RecommendationEngine
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
        
        # 1. Translate raw Neo4j JSON -> Core InfrastructureGraph via Adapter
        # Note: In the future, we could have an EngineContext, but for now we'll just adapt the graph.
        infra_graph = Neo4jAdapter.fetch_graph(ctx.graph)
        
        # 2. Build reusable O(1) Index
        graph_index = GraphIndex.build(infra_graph)
        
        findings = []
        all_recommendations = []
        
        # 3. Precompute expensive global structures
        all_sccs = TraversalService.tarjan_scc(graph_index)
        
        # 4. Analyze every node deterministically using pure Domain engines
        for node_id in infra_graph.nodes.keys():
            # Run Dependency Engine
            analysis = DependencyEngine.analyze(infra_graph, graph_index, node_id, all_sccs=all_sccs)
            
            # Use Scoring Engine universally
            risk = ScoringEngine.calculate_risk(analysis.blast_radius, analysis.is_spof, analysis.is_isolated)
            
            # If there's high risk or a SPOF, generate an Enterprise Finding
            if risk.numeric_score >= 30.0:
                rc_analysis = RootCauseEngine.analyze(infra_graph, graph_index, node_id, analysis)
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
                    business_impact=f"A failure affects {analysis.blast_radius} downstream resources. Criticality: {analysis.business_criticality}",
                    technical_impact=f"Root Causes: {'; '.join(rc_analysis['likely_causes'])}"
                )
                findings.append(finding)
                
        duration_ms = (time.time() - start_time) * 1000
                
        return AnalyzerResult(
            analyzer_id=self.metadata.id,
            score=self.calculate_score(AnalyzerResult(analyzer_id=self.metadata.id, findings=findings)),
            summary=f"Analyzed {len(infra_graph.nodes)} nodes. Found {len(findings)} high-risk dependencies.",
            findings=findings,
            recommendations=all_recommendations,
            execution_time_ms=duration_ms,
            resources_examined=len(infra_graph.nodes)
        )

    def calculate_score(self, result: AnalyzerResult) -> int:
        return super().calculate_score(result)
