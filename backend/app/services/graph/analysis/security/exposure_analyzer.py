import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class ExposureAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, resource_id: str):
        """
        Determines whether a resource is reachable from the Internet.
        Checks for paths to an InternetGateway.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        exposure = "PRIVATE"
        internet_accessible = False
        reasons = []
        
        if not self.neo4j.driver:
            return {
                "resource": resource_id,
                "internet_accessible": False,
                "exposure": "UNKNOWN (Graph Disconnected)",
                "reason": ["Neo4j not connected"]
            }

        try:
            # Query to check if there is any path from this resource to an IGW
            # Example: EC2 -> Subnet -> RouteTable -> IGW
            query = """
            MATCH path=(n {id:$resource_id})-[:IN_SUBNET|ASSOCIATED_WITH|ROUTES_TO*1..5]->(igw:InternetGateway)
            RETURN count(path) as path_count
            """
            result = self.neo4j.query(query, resource_id=resource_id)
            if result and result[0]["path_count"] > 0:
                internet_accessible = True
                exposure = "PUBLIC"
                reasons.append("Resource resides in a public subnet with a route to an Internet Gateway")
                
            # If it's an ALB, it might be internet facing itself
            alb_query = """
            MATCH (n {id:$resource_id}:ALB)
            RETURN n.id
            """
            res_alb = self.neo4j.query(alb_query, resource_id=resource_id)
            if res_alb:
                internet_accessible = True
                exposure = "PUBLIC"
                reasons.append("Resource is an Application Load Balancer which is public by default in this context")
                
        except Exception as e:
            logger.error(f"Error checking internet exposure: {e}")
            reasons.append(str(e))
            
        if not internet_accessible:
            reasons.append("No active route paths to an Internet Gateway detected.")
            
        return {
            "resource": resource_id,
            "internet_accessible": internet_accessible,
            "exposure": exposure,
            "reason": reasons
        }
