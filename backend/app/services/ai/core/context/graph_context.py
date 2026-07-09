from typing import Dict, List

from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class GraphContext:
    """
    Pulls cloud topology and relationships from Neo4j.
    """

    def __init__(self):

        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
        except Exception as e:
            print(f"[GraphContext] Neo4j driver init failed: {e}")
            self.driver = None

    def close(self):
        if self.driver:
            self.driver.close()

    def build(self, intent) -> Dict:
        """
        Build graph context — node counts, relationship summary,
        and a sample of recent relationships.
        """

        if not self.driver:
            return {"nodes": 0, "relationships": 0, "sample": []}

        try:

            with self.driver.session() as session:

                node_count = session.run(
                    "MATCH (n) RETURN count(n) AS total"
                ).single()["total"]

                rel_count = session.run(
                    "MATCH ()-[r]->() RETURN count(r) AS total"
                ).single()["total"]

                sample_result = session.run(
                    """
                    MATCH (a)-[r]->(b)
                    RETURN
                        a.id AS from_id,
                        type(r) AS relationship,
                        b.id AS to_id,
                        b.resource_type AS to_type
                    LIMIT 20
                    """
                )

                sample = [dict(record) for record in sample_result]

            return {
                "nodes": node_count,
                "relationships": rel_count,
                "sample": sample
            }

        except Exception as e:

            print(f"[GraphContext] build failed: {e}")
            return {"nodes": 0, "relationships": 0, "sample": []}
