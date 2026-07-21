"""DependencyAnalyzer – Identifies downstream/upstream dependency chains and orphan resources.

Analyzes the raw graph data provided by GraphProvider (which now includes
'upstream' and 'downstream' lists) to calculate blast radius and critical dependencies.
"""

from typing import Any, Dict

from .base_analyzer import BaseAnalyzer
from ..models import AIContext, AnalyzerResult


class DependencyAnalyzer(BaseAnalyzer):
    """Identifies downstream/upstream dependency chains and orphan resources."""

    name = "dependency"

    def analyze(self, context: AIContext) -> AnalyzerResult:
        """Perform dependency analysis on graph data."""
        
        graph_data = context.graph
        if not graph_data:
            return AnalyzerResult(
                status="skipped",
                analyzer=self.name,
                reason="No graph data available in context.",
                findings=[],
                summary="",
            )
            
        upstream = graph_data.get("upstream", [])
        downstream = graph_data.get("downstream", [])
        resource = graph_data.get("resource", {})
        resource_id = resource.get("resource_id", "Unknown")
        
        findings = []
        
        # Blast Radius (Downstream)
        downstream_count = len(downstream)
        if downstream_count > 0:
            severity = "HIGH" if downstream_count > 10 else ("MEDIUM" if downstream_count > 3 else "LOW")
            
            critical_types = ["aws_lb", "aws_autoscaling_group", "aws_eks_cluster", "aws_api_gateway_rest_api"]
            critical_impact = [d for d in downstream if any(t in str(d.get("labels", [])) for t in critical_types) or any(t in str(d.get("m_type", "")) for t in critical_types)]
            
            desc = f"Failure affects {downstream_count} downstream resources."
            if critical_impact:
                desc += f" This includes critical components such as {len(critical_impact)} load balancers or clusters."
                severity = "CRITICAL"
                
            findings.append({
                "severity": severity,
                "title": "Blast Radius",
                "description": desc,
                "metadata": {
                    "downstream_count": downstream_count,
                    "critical_impact_count": len(critical_impact)
                }
            })
            
        # Upstream Dependencies (Single Point of Failure check)
        upstream_count = len(upstream)
        if upstream_count > 0:
            findings.append({
                "severity": "INFO",
                "title": "Upstream Dependencies",
                "description": f"This resource depends on {upstream_count} upstream resources to function properly.",
                "metadata": {
                    "upstream_count": upstream_count
                }
            })
            
        # Isolation check
        if downstream_count == 0 and upstream_count == 0:
            findings.append({
                "severity": "LOW",
                "title": "Isolated Resource",
                "description": "This resource has no upstream or downstream dependencies in the graph. It may be orphaned or unused."
            })

        return AnalyzerResult(
            status="success",
            analyzer=self.name,
            findings=findings,
            metadata={
                "blast_radius_size": downstream_count,
                "upstream_dependency_size": upstream_count,
                "is_isolated": (downstream_count == 0 and upstream_count == 0)
            },
        )
