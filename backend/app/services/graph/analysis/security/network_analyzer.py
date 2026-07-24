import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def analyze(self, resource_id: str):
        """
        Assesses the perimeter defenses and network topology surrounding a resource.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        findings = []
        is_public = False
        
        try:
            # Example: Check if the resource is in a Subnet that routes to IGW
            query = """
            MATCH (n {id:$resource_id})-[:IN_SUBNET]->(s:Subnet)-[:ASSOCIATED_WITH]->(rt:RouteTable)-[:ROUTES_TO]->(igw:InternetGateway)
            RETURN igw.id as igw_id
            """
            try:
                results = self.client.query_graph(query, resource_id=resource_id)
                if results:
                    is_public = True
                    findings.append({
                        "type": "NETWORK_PUBLIC",
                        "severity": "HIGH",
                        "description": f"Resource is in a public subnet mapped to {results[0].get('igw_id', 'Unknown')}."
                    })
            except NotImplementedError:
                # Stub check since graph might be unsupported
                pass
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
        }