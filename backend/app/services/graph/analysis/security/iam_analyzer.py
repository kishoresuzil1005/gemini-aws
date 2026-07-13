import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class IAMAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, role_id: str):
        """
        Analyzes an IAM Role for excessive permissions and usage.
        """
        if not self.neo4j.node_exists(role_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        findings = []
        severity = "LOW"
        
        # MOCK POLICY ANALYSIS
        findings.append({
            "type": "MOCK_IAM_ANALYSIS",
            "severity": "HIGH",
            "description": "Mock finding: AdministratorAccess might be attached. Verify in AWS console."
        })
        severity = "HIGH"
        
        usage_count = 0
        used_by = []
        if self.neo4j.driver:
            try:
                query = """
                MATCH (r)-[:USES_ROLE]->(role:IAM_ROLE {id:$role_id})
                RETURN r.id as id, labels(r)[0] as type
                """
                results = self.neo4j.query(query, role_id=role_id)
                for res in results:
                    used_by.append({"resource": res["id"], "type": res["type"]})
                usage_count = len(used_by)
            except Exception as e:
                logger.error(f"Error querying IAM usage: {e}")
                
        return {
            "resource": role_id,
            "risk_severity": severity,
            "usage_count": usage_count,
            "used_by": used_by,
            "findings": findings
        