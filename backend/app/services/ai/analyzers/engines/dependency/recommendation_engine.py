"""
Recommendation Engine.
Generates structured deterministic recommendations based on dependency findings.
"""
from typing import List
from app.services.ai.analyzers.base.analyzer_models import AnalyzerRecommendation
from app.services.ai.analyzers.engines.dependency.dependency_models import DependencyAnalysis

class RecommendationEngine:
    
    @classmethod
    def generate(cls, analysis: DependencyAnalysis) -> List[AnalyzerRecommendation]:
        """
        Deterministically evaluates findings and produces enterprise recommendations.
        """
        recommendations = []
        
        if analysis.is_spof:
            recommendations.append(AnalyzerRecommendation(
                title="Eliminate Single Point of Failure",
                description=f"Deploy additional instances of {analysis.node_type} in multiple Availability Zones to ensure high availability.",
                priority="SHORT_TERM",
                estimated_effort="Medium",
                automation_possible=True,
                automation_script=f"aws autoscaling update-auto-scaling-group --auto-scaling-group-name {analysis.node_id}-asg --min-size 2 --max-size 4 --availability-zones us-east-1a us-east-1b",
                estimated_risk_reduction="High - Eliminates Zone Failure Risk",
                estimated_downtime="Zero downtime (Rolling Update)",
                rollback_available=True,
                approval_required=True,
                metadata={
                    "Terraform": 'resource "aws_autoscaling_group" "main" { vpc_zone_identifier = [var.subnet_a, var.subnet_b] }',
                    "Runbook": "https://wiki.corp.internal/runbooks/spof-remediation",
                    "Implementation Steps": [
                        "1. Identify secondary subnets in alternate AZs.",
                        "2. Update Auto Scaling Group or Load Balancer target groups.",
                        "3. Ensure data replication is active (if database)."
                    ],
                    "Rollback Steps": [
                        "1. Reduce min/max capacity back to 1.",
                        "2. Remove secondary subnets from Target Group."
                    ]
                }
            ))
            
        if analysis.cycles:
            recommendations.append(AnalyzerRecommendation(
                title="Break Circular Dependency",
                description="Refactor architecture to decouple services and eliminate cyclic references that cause infinite loops or deadlocks.",
                priority="IMMEDIATE",
                estimated_effort="High",
                automation_possible=False,
                estimated_risk_reduction="Critical - Prevents cascading deadlocks",
                estimated_downtime="Requires Scheduled Maintenance window",
                rollback_available=False,
                approval_required=True,
                metadata={
                    "Runbook": "https://wiki.corp.internal/runbooks/arch-decoupling",
                    "Implementation Steps": [
                        "1. Introduce an event bus (EventBridge/SQS) to decouple the cycle.",
                        "2. Update service A to publish events instead of calling service B synchronously.",
                        "3. Update service B to consume events asynchronously."
                    ]
                }
            ))
            
        if analysis.blast_radius > 50:
            recommendations.append(AnalyzerRecommendation(
                title="Reduce Blast Radius (Bulkhead Pattern)",
                description="Implement circuit breakers and decouple downstream dependencies to prevent massive cascading failures.",
                priority="LONG_TERM",
                estimated_effort="High",
                automation_possible=False,
                estimated_risk_reduction="Medium - Limits lateral impact of failure",
                estimated_downtime="Zero (Application level routing change)",
                rollback_available=True,
                approval_required=True,
                metadata={
                    "Implementation Steps": [
                        "1. Implement Circuit Breaker pattern in the application mesh.",
                        "2. Set concurrency limits on downstream lambda/API calls.",
                        "3. Add degraded fallback responses."
                    ]
                }
            ))
            
        return recommendations
