import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, resource_id: str):
        """
        Assesses the perimeter defenses and network topology surrounding a resource.
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        findings = []
        is_public = False
        
        if self.neo4j.driver:
            try:
                # Example: Check if the resource is in a Subnet that routes to IGW
                query = """
                MATCH (n {id:$resource_id})-[:IN_SUBNET]->(s:Subnet)-[:ASSOCIATED_WITH]->(rt:RouteTable)-[:ROUTES_TO]->(igw:InternetGateway)
                RETURN igw.id as igw_id
                """
                results = self.neo4j.query(query, resource_id=resource_id)
                if results:
                    is_public = True
                    findings.append({
                        "type": "NETWORK_PUBLIC",
                        "severity": "HIGH",
                        "description": f"Resource is in a public subnet mapped to {results[0]['igw_id']}."
                    })
            except Exception as e:
                logger.error(f"Error querying network topology: {e}")
                
        if not is_public:
            findings.append({
                "type": "NETWORK_PRIVATE",
                "severity": "LOW",
                "description": "Resource is isolated in a private subnet with no direct IGW route."
            })
            
        return {
            "resource": resource_id,
            "network_type": "PUBLIC" if is_public else "PRIVATE",
            "findings": findings
        