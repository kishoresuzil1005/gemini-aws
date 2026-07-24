import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer
from exceptions.analyzer_exceptions import KnowledgeNotFoundError

logger = logging.getLogger(__name__)

class CostAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()
        self.dependency_analyzer = DependencyAnalyzer(self.client)

    def analyze(self, root_resource_id: str):
        """
        Calculates total application-level cost by finding all downstream
        resources and aggregating their costs using the Rule Catalog (pricing).
        """
        resource = self.client.get_resource(root_resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream = self.dependency_analyzer.get_downstream(root_resource_id, depth=10)
        
        # Include the root resource itself
        downstream.append({"id": root_resource_id, "labels": ["ApplicationRoot"]})
        
        # Fetch cost rules from Knowledge Service
        cost_rules = self.client.get_rules(category="cost")
        # Build a simple pricing lookup map: resource_type -> estimated_cost
        pricing_map = {}
        for rule in cost_rules:
            res_type = rule.get("resource_type")
            if res_type:
                pricing_map[res_type] = rule.get("estimated_cost", 0)
        
        # Fallback values if rule catalog is empty for these types
        default_pricing = {
            "EC2": 100,
            "RDS": 200,
            "ALB": 50,
            "Lambda": 85,
            "NATGateway": 32,
            "DynamoDBTable": 15
        }
        
        total_cost = 0
        breakdown = []
        
        for item in downstream:
            labels = item.get("labels", [])
            label = labels[0] if labels else "Unknown"
            
            # Lookup cost in KS rules, fallback to default, then 5
            cost = pricing_map.get(label, default_pricing.get(label, 5))
                
            total_cost += cost
            breakdown.append({
                "resource": item.get("id"),
                "type": label,
                "estimated_monthly_cost": cost
            })
            
        return {
            "application_root": root_resource_id,
            "total_monthly_cost": total_cost,
            "breakdown": breakdown
        }