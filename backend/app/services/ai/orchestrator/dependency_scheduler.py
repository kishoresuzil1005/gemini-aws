from typing import List
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.orchestrator.orchestration_models import ExecutionStep

class DependencyScheduler:
    def __init__(self, neo4j_service: Neo4jService = None):
        self.neo4j = neo4j_service or Neo4jService()

    def schedule(self, resource_id: str, steps: List[ExecutionStep]) -> List[ExecutionStep]:
        # Connect to Neo4j to check dependencies
        # e.g., MATCH (n {id: resource_id})<-[:INVOKES]-(upstream)
        upstream_resources = []
        if self.neo4j.driver:
            try:
                res = self.neo4j.query(
                    "MATCH (n {id: $resource_id})<-[]-(u) RETURN u.id as id, labels(u)[0] as type",
                    resource_id=resource_id
                )
                for r in res:
                    upstream_resources.append(r["type"])
            except Exception:
                pass
                
        # If there are upstream resources, we might need to gracefully stop them first, or at least acknowledge
        if upstream_resources:
            dependency_step = ExecutionStep(
                id="step-dep", title=f"Notify upstream services ({', '.join(upstream_resources)})", action="Notify",
                command="echo 'Upstream dependencies detected'", estimated_time="1m", rollback="N/A"
            )
            # Insert at the beginning
            steps.insert(0, dependency_step)
            
        return steps
