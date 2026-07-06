import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class SecurityGroupAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, resource_id: str):
        """
        Analyzes a Security Group for risky open ports and maps 
        which compute resources rely on it.
        """
        if not self.neo4j.node_exists(resource_id):
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

        # Check Usage via Neo4j
        usage_count = 0
        used_by = []
        if self.neo4j.driver:
            try:
                query = """
                MATCH (r)-[:USES_SG]->(sg:SecurityGroup {id:$resource_id})
                RETURN r.id as id, labels(r)[0] as type
                """
                results = self.neo4j.query(query, resource_id=resource_id)
                for res in results:
                    used_by.append({"resource": res["id"], "type": res["type"]})
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
