"""
Explainability Engine.
Generates deterministic reasoning for findings, priorities, and root causes without an LLM.
"""
from typing import Dict, Any
from .dependency_models import DependencyAnalysis

class ExplainabilityEngine:
    
    @classmethod
    def generate_explanation(cls, analysis: DependencyAnalysis, impact: Dict[str, Any]) -> Dict[str, str]:
        """
        Produces human-readable, deterministic explanations.
        """
        why_happened = f"The resource {analysis.node_id} failed or degraded, which cascaded to {analysis.blast_radius} downstream dependencies."
        if analysis.is_spof:
            why_happened = f"The resource {analysis.node_id} is a Single Point of Failure (SPOF) with no redundancy. Its failure cascades to {analysis.blast_radius} dependencies."
            
        why_matters = f"This failure causes a {impact.get('business_impact', 'Low')} business impact and affects {impact.get('affected_applications', 0)} applications."
        
        evidence = f"Topological traversal detected {analysis.upstream_count} upstream dependencies and a dependency depth of {analysis.dependency_depth}."
        if analysis.cycles:
            evidence += f" Additionally, {len(analysis.cycles)} circular dependency loops were detected, heavily increasing deadlock risk."
            
        confidence_explanation = "High confidence (100) based on deterministic directed acyclic graph traversal and explicit VPC topological rules."
        
        return {
            "why_it_happened": why_happened,
            "why_it_matters": why_matters,
            "evidence": evidence,
            "how_calculated": "Calculated via O(V+E) graph traversal without stochastic ML interference.",
            "confidence_explanation": confidence_explanation,
            "priority_explanation": f"Priority determined by risk score ({analysis.risk_score}) and criticality ({analysis.criticality_score})."
        }
