import logging
from fastapi import HTTPException
from knowledge.service.client_factory import get_default_client

logger = logging.getLogger(__name__)

class IAMAnalyzer:
    def __init__(self, knowledge_client=None):
        self.client = knowledge_client or get_default_client()

    def analyze(self, role_id: str):
        """
        Analyzes an IAM Role for excessive permissions and usage.
        """
        resource = self.client.get_resource(role_id)
        if not resource:
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
        try:
            query = """
            MATCH (r)-[:USES_ROLE]->(role:IAM_ROLE {id:$role_id})
            RETURN r.id as id, labels(r)[0] as type
            """
            try:
                results = self.client.query_graph(query, role_id=role_id)
                for res in results:
                    used_by.append({"resource": res.get("id"), "type": res.get("type")})
                usage_count = len(used_by)
            except NotImplementedError:
                # Fallback if graph query is unsupported
                # We could try to use get_relationships and filter by USES_ROLE
                rels = self.client.get_relationships(role_id)
                for rel in rels:
                    if rel.get("type") == "USES_ROLE" and rel.get("target") == role_id:
                        used_by.append({"resource": rel.get("source"), "type": "Unknown"})
                usage_count = len(used_by)
        except Exception as e:
            logger.error(f"Error querying IAM usage: {e}")
                
        return {
            "resource": role_id,
            "risk_severity": severity,
            "usage_count": usage_count,
            "used_by": used_by,
            "findings": findings
        }