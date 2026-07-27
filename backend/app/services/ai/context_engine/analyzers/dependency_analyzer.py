"""DependencyAnalyzer – Identifies downstream/upstream dependency chains and orphan resources.

Analyzes the raw graph data provided by GraphProvider (which now includes
'upstream' and 'downstream' lists) to calculate blast radius and critical dependencies.
"""

from collections import defaultdict, deque
from typing import Any, Dict, List, Set

from .base_analyzer import BaseAnalyzer
from ..models import AIContext, AnalyzerResult
from app.services.ai.context_engine.graph.relationship_categories import get_category


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
        nodes = {n.get("id"): n for n in subgraph.get("nodes", [])}
        
        incoming_edges = [e for e in edges if e.get("target") == resource_id]
        outgoing_edges = [e for e in edges if e.get("source") == resource_id]
        
        upstream_count = len(incoming_edges)
        downstream_count = len(outgoing_edges)
        relationship_count = len(incoming_edges) + len(outgoing_edges)
        
        connected_resources = {e.get("source") for e in edges if e.get("target") == resource_id} | \
                              {e.get("target") for e in edges if e.get("source") == resource_id}
        
        unique_targets = {e.get("target") for e in outgoing_edges}
        blast_radius_size = len(unique_targets)
        
        relationship_types = list(set([e.get("relationship") for e in edges if e.get("source") == resource_id or e.get("target") == resource_id]))
        
        dependency_depth = self._calculate_bfs_depth(resource_id, edges)
        
        dependency_summary = defaultdict(list)
        findings = []
        
        # Categorize dependencies
        for e in outgoing_edges:
            target_id = e.get("target")
            rel = e.get("relationship")
            category = get_category(rel)
            target_node = nodes.get(target_id, {})
            target_name = target_node.get("name") or target_id
            target_type = target_node.get("type", "Unknown")
            
            dependency_summary[category.lower()].append(f"{target_type} {target_name}")
            
        # Also group incoming edges (some things depend on us)
        for e in incoming_edges:
            source_id = e.get("source")
            rel = e.get("relationship")
            category = get_category(rel)
            source_node = nodes.get(source_id, {})
            source_name = source_node.get("name") or source_id
            source_type = source_node.get("type", "Unknown")
            
            # Label incoming specifically so it's clear
            dependency_summary[category.lower()].append(f"[Incoming] {source_type} {source_name}")

        # Shared resources and critical dependencies logic
        target_incoming_counts = defaultdict(int)
        for e in edges:
            target_incoming_counts[e.get("target")] += 1
            
        critical_dependencies = [n for n, count in target_incoming_counts.items() if count > 1]
        shared_resources = [n for n, count in target_incoming_counts.items() if count > 1 and n in unique_targets]
        
        is_isolated = relationship_count == 0
        
        if is_isolated:
            findings.append({
                "severity": "LOW",
                "title": "Isolated Resource",
                "description": "This resource has no upstream or downstream dependencies in the graph. It may be orphaned or unused."
            })
        else:
            for cat, items in dependency_summary.items():
                if items:
                    findings.append({
                        "severity": "INFO",
                        "title": f"{cat.title()} Dependencies",
                        "description": f"Found {len(items)} {cat.lower()} relationship(s).",
                        "evidence": list(set(items))
                    })
                    
        return AnalyzerResult(
            status="success",
            analyzer=self.name,
            findings=findings,
            metadata={
                "is_isolated": is_isolated,
                "relationship_count": relationship_count,
                "relationship_types": relationship_types,
                "connected_resource_count": len(connected_resources),
                "upstream_dependency_size": upstream_count,
                "downstream_dependency_size": downstream_count,
                "blast_radius_size": blast_radius_size,
                "dependency_depth": dependency_depth,
                "critical_dependencies": critical_dependencies,
                "shared_resources": shared_resources,
                "dependency_summary": dict(dependency_summary)
            },
        )

    def _calculate_bfs_depth(self, start_id: str, edges: List[Dict[str, Any]]) -> int:
        if not start_id or not edges:
            return 0
            
        adj = defaultdict(list)
        for e in edges:
            # Directed graph downstream BFS
            adj[e.get("source")].append(e.get("target"))
            
        visited = set([start_id])
        queue = deque([(start_id, 0)])
        max_depth = 0
        
        while queue:
            curr, depth = queue.popleft()
            max_depth = max(max_depth, depth)
            
            for nxt in adj[curr]:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, depth + 1))
                    
        return max_depth
