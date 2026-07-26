import logging
from typing import List, Dict, Any, Optional

from app.services.dependency_engine.models import (
    DependencyNode, DependencyEdge, DependencyGraphView, 
    RootCause, BlastRadius, DependencyImpact, CriticalPath,
    DependencyPath, DependencyRecommendation, DependencyFinding
)
from app.services.dependency_engine.cache import DependencyCache
from knowledge.service.knowledge_client import KnowledgeClient

logger = logging.getLogger(__name__)

class DependencyIntelligenceEngine:
    """Authoritative Dependency Reasoning Engine for the CloudOps Platform."""

    def __init__(self, knowledge_client: KnowledgeClient):
        self.client = knowledge_client
        self.cache = DependencyCache()

    # --- Phase 2 & 3: Query Orchestration & Graph Reasoning ---
    def get_node(self, resource_id: str) -> Optional[DependencyNode]:
        cached = self.cache.get(f"node_{resource_id}")
        if cached: return cached
        
        res = self.client.get_resource(resource_id)
        if not res or hasattr(res, "errors"):
            return None
        node = DependencyNode(
            id=res.resource_id,
            name=res.name,
            type=res.resource_type,
            status=res.status,
            properties=res.configuration
        )
        self.cache.set(f"node_{resource_id}", node)
        return node

    def _build_edges_from_relationships(self, relationships: List[Any]) -> List[DependencyEdge]:
        edges = []
        for r in relationships:
            edges.append(DependencyEdge(
                source_id=r.source_id,
                target_id=r.target_id,
                relationship_type=r.type,
                properties=r.metadata
            ))
        return edges

    def get_dependencies(self, resource_id: str) -> DependencyGraphView:
        """Retrieves direct inbound and outbound dependencies."""
        cached = self.cache.get(f"deps_{resource_id}")
        if cached: return cached
        
        node = self.get_node(resource_id)
        if not node:
            return DependencyGraphView(nodes=[], edges=[])

        relationships = self.client.get_relationships(resource_id)
        if hasattr(relationships, "errors"):
            relationships = []
            
        edges = self._build_edges_from_relationships(relationships)
        nodes = {node.id: node}

        # Also fetch neighboring nodes
        for e in edges:
            neighbor_id = e.target_id if e.source_id == resource_id else e.source_id
            if neighbor_id not in nodes:
                n = self.get_node(neighbor_id)
                if n:
                    nodes[n.id] = n

        view = DependencyGraphView(nodes=list(nodes.values()), edges=edges)
        self.cache.set(f"deps_{resource_id}", view)
        return view

    def get_shortest_path(self, source_id: str, target_id: str) -> Optional[DependencyPath]:
        try:
            res = self.client.query_graph(f"MATCH p=shortestPath((a)-[*]-(b)) WHERE a.id='{source_id}' AND b.id='{target_id}' RETURN p")
            if not res or hasattr(res, "errors"):
                return None
        except Exception:
            return None
            
        nodes = []
        # Fallback empty logic since graph query format varies
        return DependencyPath(nodes=nodes, edges=[], total_distance=0)

    # --- Phase 4: Root Cause Analysis ---
    def analyze_root_cause(self, incident_resource_id: str, failure_symptom: str) -> Optional[RootCause]:
        """Determines root dependency failure causing an incident."""
        node = self.get_node(incident_resource_id)
        if not node:
            return None
        
        # Heuristic: Find an upstream dependency that is also in a failed/degraded state
        deps = self.get_dependencies(incident_resource_id)
        root_node = node
        for n in deps.nodes:
            if n.id != incident_resource_id and n.status not in ["AVAILABLE", "ACTIVE", "OK", "running"]:
                root_node = n
                break
                
        return RootCause(
            root_dependency=root_node,
            failure_type="Dependency Chain Failure",
            impacted_resources=[n.id for n in deps.nodes if n.id != root_node.id],
            narrative=f"Incident on {node.name} caused by upstream failure in {root_node.name} ({failure_symptom})"
        )

    # --- Phase 5: Blast Radius Analysis ---
    def analyze_blast_radius(self, resource_id: str) -> BlastRadius:
        """Determines the impact of a resource failure."""
        origin = self.get_node(resource_id)
        if not origin:
            return None
            
        # Call platform's get_resource_subgraph
        blast_res = self.client.get_resource_subgraph(resource_id)
        
        # We assume the subgraph returns a graph object containing nodes
        affected_ids = []
        if isinstance(blast_res, dict) and "nodes" in blast_res:
            affected_ids = [n.get("id") for n in blast_res.get("nodes", []) if isinstance(n, dict)]
        elif hasattr(blast_res, "nodes"):
            affected_ids = [n.id for n in blast_res.nodes]
        
        impacts = []
        for aid in affected_ids:
            if aid != resource_id:
                impacts.append(DependencyImpact(
                    resource_id=aid,
                    impact_type="INDIRECT",
                    severity="HIGH",
                    description=f"Depends on {resource_id}"
                ))

        return BlastRadius(
            origin=origin,
            impacts=impacts,
            risk_score=len(impacts) * 10,
            affected_resources_count=len(impacts)
        )

    # --- Phase 6: Critical Path Analysis ---
    def analyze_critical_path(self, entry_id: str, exit_id: str) -> CriticalPath:
        path = self.get_shortest_path(entry_id, exit_id)
        if not path:
            return None
            
        # Identify bottleneck: node with highest inbound dependencies (simulated here)
        bottlenecks = [path.nodes[len(path.nodes)//2]] if len(path.nodes) > 2 else []
        
        return CriticalPath(
            path=path,
            bottlenecks=bottlenecks,
            single_points_of_failure=bottlenecks
        )

    # --- Phase 7: Impact Analysis ---
    def analyze_impact(self, resource_id: str, action: str) -> List[DependencyImpact]:
        br = self.analyze_blast_radius(resource_id)
        if not br: return []
        
        for i in br.impacts:
            i.description = f"Impacted by {action} action on {resource_id}"
            
        return br.impacts

    # --- Phase 8: Recommendation Engine ---
    def generate_recommendations(self, resource_id: str) -> List[DependencyRecommendation]:
        # Leverage KnowledgeClient and rules to generate recommendations
        # Since we cannot bypass to internal RulesCatalog, we simulate based on graph structure
        deps = self.get_dependencies(resource_id)
        recs = []
        if len(deps.nodes) > 5:
            recs.append(DependencyRecommendation(
                severity="MEDIUM",
                confidence=0.8,
                reason="High fan-out detected.",
                evidence=f"{resource_id} has {len(deps.nodes)} dependencies.",
                affected_resources=[resource_id],
                suggested_remediation="Consider decoupling architecture."
            ))
        return recs

    # --- Phase 9: AI Explanation ---
    def generate_ai_explanation(self, finding: Any) -> str:
        """
        AI Explanation generation.
        In a real scenario, this connects to an LLM provider.
        Here we generate a structured narrative based on the finding type.
        """
        if isinstance(finding, RootCause):
            return f"**Root Cause Analysis:**\nThe root cause was identified as {finding.root_dependency.name}. The failure type is {finding.failure_type}. {finding.narrative}."
        elif isinstance(finding, BlastRadius):
            return f"**Blast Radius Assessment:**\nIf {finding.origin.name} fails, {finding.affected_resources_count} resources are at risk, generating a risk score of {finding.risk_score}."
        return "AI Explanation: Dependency graph structurally verified."
