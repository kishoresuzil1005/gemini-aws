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
            
        resource = graph_data.get("resource", {})
        resource_id = resource.get("resource_id", "Unknown")
        
        subgraph = graph_data.get("subgraph", {})
        edges = subgraph.get("edges", [])
        
        # Calculate incoming and outgoing edges for this resource
        # Upstream: things this resource depends on (Incoming to resource OR outgoing from resource? wait.
        # "Incoming edge: edge.target == resource_id. Outgoing edge: edge.source == resource_id."
        # "Upstream Dependencies: Number of incoming edges. Downstream Dependencies: Number of outgoing edges."
        
        incoming_edges = [e for e in edges if e.get("target") == resource_id]
        outgoing_edges = [e for e in edges if e.get("source") == resource_id]
        
        upstream_count = len(incoming_edges)
        downstream_count = len(outgoing_edges)
        
        findings = []
        
        # Blast Radius (Downstream)
        if downstream_count > 0:
            # Blast radius size = Number of unique directly connected resources (downstream targets)
            unique_targets = {e.get("target") for e in outgoing_edges}
            blast_radius_size = len(unique_targets)
            
            severity = "HIGH" if blast_radius_size > 10 else ("MEDIUM" if blast_radius_size > 3 else "LOW")
            
            # Try to identify critical impact based on target node metadata if available
            critical_types = ["aws_lb", "aws_autoscaling_group", "aws_eks_cluster", "aws_api_gateway_rest_api"]
            nodes = {n.get("id"): n for n in subgraph.get("nodes", [])}
            critical_impact = [nodes[t] for t in unique_targets if t in nodes and (any(ct in str(nodes[t].get("labels", [])) for ct in critical_types) or any(ct in str(nodes[t].get("type", "")) for ct in critical_types))]
            
            desc = f"Failure affects {blast_radius_size} downstream resources."
            if critical_impact:
                desc += f" This includes critical components such as {len(critical_impact)} load balancers or clusters."
                severity = "CRITICAL"
                
            findings.append({
                "severity": severity,
                "title": "Blast Radius",
                "description": desc,
                "metadata": {
                    "downstream_count": downstream_count,
                    "blast_radius_size": blast_radius_size,
                    "critical_impact_count": len(critical_impact)
                }
            })
        else:
            blast_radius_size = 0
            
        # Upstream Dependencies
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
        is_isolated = (incoming_edges == [] and outgoing_edges == [])
        if is_isolated:
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
                "blast_radius_size": blast_radius_size,
                "upstream_dependency_size": upstream_count,
                "downstream_dependency_size": downstream_count,
                "is_isolated": is_isolated
            },
        )
