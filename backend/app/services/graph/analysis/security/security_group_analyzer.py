import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class SecurityGroupAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def analyze(self, resource_id: str):
        """
        Analyzes a Security Group for risky open ports and maps 
        which compute resources rely on it.
        """
        resource = self.client.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
            
        findings = []
        severity = "LOW"
        
        # MOCK PORT ANALYSIS
        # In the future, this would query the `resource_metadata` JSON blob 
        # from PostgreSQL or inspect `n.inbound_rules` if embedded in Neo4j.
        findings.append({
            "type": "MOCK_PORT_ANALYSIS",
            "severity": "HIGH",
            "description": "Mock finding: SSH (Port 22) might be open to 0.0.0.0/0. Verify rules in AWS console."
        })
        severity = "HIGH"

        # Check Usage via KnowledgeClient
        usage_count = 0
        used_by = []
        try:
            query = """
            MATCH (r)-[:USES_SG]->(sg:SecurityGroup {id:$resource_id})
            RETURN r.id as id, labels(r)[0] as type
            """
            try:
                results = self.client.query_graph(query, resource_id=resource_id)
                for res in results:
                    used_by.append({"resource": res.get("id"), "type": res.get("type")})
                usage_count = len(used_by)
            except NotImplementedError:
                # Fallback if graph query is unsupported
                rels = self.client.get_relationships(resource_id)
                for rel in rels:
                    if rel.get("type") == "USES_SG" and rel.get("target") == resource_id:
                        used_by.append({"resource": rel.get("source"), "type": "Unknown"})
                usage_count = len(used_by)
        except Exception as e:
            logger.error(f"Error querying SG usage: {e}")
                
        return {
            "resource": resource_id,
            "risk_severity": severity,
            "usage_count": usage_count,
            "used_by": used_by,
            "findings": findings
        }