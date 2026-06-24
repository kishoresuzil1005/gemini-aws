from app.services.graph.neo4j_service import Neo4jService


class GraphContextBuilder:

    def __init__(self):
        self.neo4j = Neo4jService()

    def get_context(self, resource_id):

        query = """
        MATCH (n {id:$id})-[r]->(m)

        RETURN
            type(r) as relationship,
            m.id as target,
            labels(m)[0] as target_type
        """

        rows = self.neo4j.query(
            query,
            id=resource_id
        )

        return rows or []
