import logging
from app.services.graph.neo4j_service import Neo4jService

logger = logging.getLogger("GraphServiceLegacy")

class GraphService:

    @staticmethod
    def create_resource(resource):
        Neo4jService.create_resource(resource)

    @staticmethod
    def create_relationship(source_id: str, target_id: str, relationship_type: str):
        Neo4jService.create_relationship(source_id, target_id, relationship_type)

    @staticmethod
    def clear_graph():
        Neo4jService.clear_graph()
