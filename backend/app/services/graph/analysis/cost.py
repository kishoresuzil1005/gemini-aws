import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.analysis.dependency_analyzer import DependencyAnalyzer

logger = logging.getLogger(__name__)

class CostAnalyzer:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()
        self.dependency_analyzer = DependencyAnalyzer(self.neo4j)

    def analyze(self, root_resource_id: str):
        """
        Calculates total application-level cost by finding all downstream
        resources and aggregating their costs.
        Since cost data is not deeply integrated yet, this uses heuristics based on resource type.
        """
        if not self.neo4j.node_exists(root_resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        downstream = self.dependency_analyzer.get_downstream(root_resource_id, depth=10)
        
        # Include the root resource itself
        downstream.append({"id": root_resource_id, "labels": ["ApplicationRoot"]})
        
        total_cost = 0
        breakdown = []
        
        for item in downstream:
            labels = item.get("labels", [])
            label = labels[0] if labels else "Unknown"
            
            # Simple heuristic cost estimation
            cost = 0
            if label == "EC2":
                cost = 100
            elif label == "RDS":
                cost = 200
            elif label == "ALB":
                cost = 50
            elif label == "Lambda":
                cost = 85
            elif label == "NATGateway":
                cost = 32
            elif label == "DynamoDBTable":
                cost = 15
            else:
                cost = 5
                
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
