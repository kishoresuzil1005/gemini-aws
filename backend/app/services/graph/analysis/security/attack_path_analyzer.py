import logging
from fastapi import HTTPException
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger(__name__)

class AttackPathAnalyzer:
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j = neo4j_service

    def analyze(self, resource_id: str):
        """
        Executes an end-to-end traversal simulating a potential breach.
        Finds paths from this resource to sensitive targets (like RDS, S3, Secrets).
        """
        if not self.neo4j.node_exists(resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
            
        attack_paths = []
        risk = "LOW"
        
        if self.neo4j.driver:
            try:
                # Mock logical traversal query finding downstream sensitive databases
                query = """
                MATCH path=(start {id:$resource_id})-[*1..5]->(target)
                WHERE labels(target)[0] IN ['RDS', 'DynamoDBTable', 'S3Bucket']
                RETURN [n IN nodes(path) | {id: n.id, type: labels(n)[0]}] AS path_nodes
                LIMIT 5
                """
                results = self.neo4j.query(query, resource_id=resource_id)
                for res in results:
                    attack_paths.append(res["path_nodes"])
                    risk = "HIGH"
            except Exception as e:
                logger.error(f"Error executing attack path query: {e}")
                
        return {
            "resource": resource_id,
            "risk_level": risk,
            "paths": attack_paths
        