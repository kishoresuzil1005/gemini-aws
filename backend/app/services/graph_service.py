import logging
from app.database_neo4j import driver

logger = logging.getLogger("GraphService")

class GraphService:

    @staticmethod
    def create_resource(resource):
        """
        Inserts or merges a resource node in the Neo4j graph database.
        """
        if not driver:
            logger.warning("Neo4j driver is not initialized. Skipping create_resource.")
            return

        query = """
        MERGE (r:Resource {
            resource_id: $resource_id
        })
        SET r.resource_type = $resource_type,
            r.name = $name,
            r.region = $region,
            r.status = $status
        """
        try:
            with driver.session() as session:
                session.run(
                    query,
                    resource_id=resource["resource_id"],
                    resource_type=resource["resource_type"],
                    name=resource.get("resource_name") or resource.get("name") or "Unknown",
                    region=resource.get("region") or "global",
                    status=resource.get("status") or "active"
                )
        except Exception as e:
            logger.error(f"Error merging resource node {resource.get('resource_id')} in Neo4j: {e}")

    @staticmethod
    def create_relationship(source_id: str, target_id: str, relationship_type: str):
        """
        Establishes a directed relationship between two resource id nodes in the Neo4j database.
        """
        if not driver:
            logger.warning("Neo4j driver is not initialized. Skipping create_relationship.")
            return

        # Sanitize relationship type for Cypher inject
        safe_rel_type = "".join(c for c in relationship_type if c.isalnum() or c == "_").upper()
        if not safe_rel_type:
            safe_rel_type = "RELATED_TO"

        query = f"""
        MATCH (source:Resource {{resource_id: $source_id}})
        MATCH (target:Resource {{resource_id: $target_id}})
        MERGE (source)-[r:{safe_rel_type}]->(target)
        """
        try:
            with driver.session() as session:
                session.run(
                    query,
                    source_id=source_id,
                    target_id=target_id
                )
        except Exception as e:
            logger.error(f"Error creating relationship ({source_id})-[{safe_rel_type}]->({target_id}) in Neo4j: {e}")

    @staticmethod
    def clear_graph():
        """
        Completely clears the Neo4j database. Helpful for fresh re-scans.
        """
        if not driver:
            return
        query = "MATCH (n) DETACH DELETE n"
        try:
            with driver.session() as session:
                session.run(query)
        except Exception as e:
            logger.error(f"Exception trying to clear Neo4j graph: {e}")
