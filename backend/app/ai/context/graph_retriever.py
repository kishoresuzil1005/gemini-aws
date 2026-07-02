from typing import List, Dict, Any

from neo4j import GraphDatabase

from app.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD


class GraphRetriever:
    """
    Retrieves cloud infrastructure topology from Neo4j.

    This class is responsible for fetching neighbouring resources,
    relationships and dependency chains for AI reasoning.
    """

    def __init__(self):

        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(
                NEO4J_USER,
                NEO4J_PASSWORD
            )
        )

    def close(self):
        self.driver.close()

    def get_neighbors(
        self,
        resource_id: str,
        depth: int = 2
    ) -> List[Dict[str, Any]]:

        query = f"""
        MATCH path=(n)-[r*1..{depth}]-(m)

        WHERE n.id=$resource_id

        RETURN path
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                resource_id=resource_id
            )

            paths = []

            for record in result:

                path = record["path"]

                nodes = []
                relationships = []

                for node in path.nodes:
                    nodes.append(
                        {
                            "id": node.get("id"),
                            "type": list(node.labels)[0] if node.labels else None,
                            "name": node.get("name"),
                        }
                    )

                for rel in path.relationships:
                    relationships.append(
                        {
                            "type": rel.type,
                            "from": rel.start_node.get("id"),
                            "to": rel.end_node.get("id"),
                        }
                    )

                paths.append(
                    {
                        "nodes": nodes,
                        "relationships": relationships,
                    }
                )

            return paths

    def get_resource(
        self,
        resource_id: str
    ) -> Dict:

        query = """
        MATCH (n)

        WHERE n.id=$resource_id

        RETURN n
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                resource_id=resource_id
            ).single()

            if not result:
                return {}

            node = result["n"]

            return dict(node)

    def get_resources_by_type(
        self,
        resource_type: str
    ) -> List[Dict]:

        query = f"""
        MATCH (n:{resource_type})

        RETURN n
        """

        with self.driver.session() as session:

            result = session.run(query)

            return [
                dict(record["n"])
                for record in result
            ]

    def get_relationships(
        self,
        resource_id: str
    ) -> List[Dict]:

        query = """
        MATCH (a)-[r]->(b)

        WHERE a.id=$resource_id

        RETURN
            type(r) AS relationship,
            b.id AS target,
            labels(b)[0] AS target_type,
            b.name AS target_name
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                resource_id=resource_id
            )

            return [
                dict(record)
                for record in result
            ]
