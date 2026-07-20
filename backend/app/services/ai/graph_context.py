from app.services.graph.neo4j_service import Neo4jService


class GraphContextBuilder:

    def __init__(self):
        self.graph = Neo4jService()

    def get_context(self, resource_id: str):
        """
        Builds the complete graph context for a resource.
        Includes:
        - Resource information
        - Outgoing relationships
        - Incoming relationships
        """

        # ----------------------------
        # Get resource information
        # ----------------------------
        resource_query = """
        MATCH (n {id:$id})
        RETURN
            n.id AS resource_id,
            labels(n)[0] AS resource_type,
            n.name AS name,
            n.provider AS provider,
            n.region AS region
        """

        resource_rows = self.graph.query(resource_query, id=resource_id)

        if not resource_rows:
            return {
                "resource": resource_id,
                "dependencies": [],
                "incoming_dependencies": []
            }

        resource = resource_rows[0]

        # ----------------------------
        # Outgoing relationships
        # ----------------------------
        outgoing_query = """
        MATCH (n {id:$id})-[r]->(m)
        RETURN
            type(r) AS relationship,
            labels(m)[0] AS resource_type,
            m.id AS resource_id,
            m.name AS name
        """

        outgoing_rows = self.graph.query(outgoing_query, id=resource_id)

        outgoing = []

        for row in outgoing_rows:
            outgoing.append({
                "relationship": row["relationship"],
                "type": row["resource_type"],
                "id": row["resource_id"],
                "name": row.get("name")
            })

        # ----------------------------
        # Incoming relationships
        # ----------------------------
        incoming_query = """
        MATCH (m)-[r]->(n {id:$id})
        RETURN
            type(r) AS relationship,
            labels(m)[0] AS resource_type,
            m.id AS resource_id,
            m.name AS name
        """

        incoming_rows = self.graph.query(incoming_query, id=resource_id)

        incoming = []

        for row in incoming_rows:
            incoming.append({
                "relationship": row["relationship"],
                "type": row["resource_type"],
                "id": row["resource_id"],
                "name": row.get("name")
            })

        return {
            "resource": resource["resource_id"],
            "resource_type": resource["resource_type"],
            "name": resource.get("name"),
            "provider": resource.get("provider"),
            "region": resource.get("region"),
            "dependencies": outgoing,
            "incoming_dependencies": incoming
        }
