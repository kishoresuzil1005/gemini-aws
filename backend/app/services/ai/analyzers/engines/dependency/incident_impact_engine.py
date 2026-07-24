"""
Incident Impact Engine.
Classifies blast radius into deterministic business, customer, and technical impacts.
"""
from typing import Dict, List, Any
from .dependency_models import DependencyAnalysis

class IncidentImpactEngine:
    
    @classmethod
    def evaluate(cls, analysis: DependencyAnalysis, downstream_nodes: List[str], infra_graph: Any) -> Dict[str, Any]:
        """
        Deterministically evaluates the multi-dimensional impact of a failure.
        """
        impact = {
            "business_impact": "Low",
            "technical_impact": "Low",
            "customer_impact": "None",
            "financial_impact": "None",
            "operational_impact": "Low",
            "affected_applications": 0,
            "affected_databases": 0,
            "affected_compute": 0,
            "affected_network": 0,
            "affected_storage": 0
        }
        
        # Categorize affected resources
        for node_id in downstream_nodes:
            props = infra_graph.nodes.get(node_id, {})
            node_type = str(props.get("type", props.get("resource_type", ""))).lower()
            
            if "db" in node_type or "rds" in node_type or "dynamodb" in node_type:
                impact["affected_databases"] += 1
            elif "ec2" in node_type or "lambda" in node_type or "ecs" in node_type or "eks" in node_type:
                impact["affected_compute"] += 1
            elif "vpc" in node_type or "gateway" in node_type or "subnet" in node_type or "route" in node_type:
                impact["affected_network"] += 1
            elif "s3" in node_type or "ebs" in node_type or "efs" in node_type:
                impact["affected_storage"] += 1
                
        # Evaluate Business & Customer Impact
        if impact["affected_databases"] > 5 or impact["affected_network"] > 10:
            impact["business_impact"] = "Critical"
            impact["operational_impact"] = "Critical"
        elif analysis.business_criticality in ["Mission Critical", "Production"]:
            impact["business_impact"] = "High"
            impact["customer_impact"] = "Direct"
            impact["financial_impact"] = "High"
        
        if analysis.blast_radius > 50:
            impact["technical_impact"] = "Critical"
        elif analysis.blast_radius > 10:
            impact["technical_impact"] = "High"
            
        impact["affected_applications"] = min(impact["affected_compute"], 1 + (impact["affected_databases"] // 2))
        
        return impact
