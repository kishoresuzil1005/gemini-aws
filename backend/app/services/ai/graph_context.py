from app.services.graph.neo4j_service import Neo4jService


class GraphContextBuilder:

    def __init__(self):
        self.graph = Neo4jService()

    def get_context(self, resource_id: str):
        query = """
        MATCH (n {id:$id})-[r]->(m)
        RETURN
            type(r) AS relationship,
            labels(m)[0] AS resource_type,
            m.id AS resource_id,
            m.name AS name
        """
        rows = self.graph.query(query, id=resource_id)

        dependencies = []
        for row in rows:
            dependencies.append({
                "relationship": row["relationship"],
                "type": row["resource_type"],
                "id": row["resource_id"],
                "name": row.get("name")
            })

        return {
            "resource": resource_id,
            "dependencies": dependencies
        }
