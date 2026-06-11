from sqlalchemy.orm import Session

from app.database import ResourceDB
from app.services.graph.neo4j_service import Neo4jService


class GraphSyncService:

    def __init__(self, db: Session):
        self.db = db
        self.graph = Neo4jService()

    def sync_resources(self):

        resources = (
            self.db.query(ResourceDB)
            .all()
        )

        synced_resources = 0

        for resource in resources:

            try:

                self.graph.create_node(
                    node_type=resource.resource_type,
                    resource_id=resource.resource_id,
                    name=resource.name or resource.resource_id,
                    provider=resource.provider
                )

                synced_resources += 1

            except Exception as e:

                print(
                    f"Graph sync failed for "
                    f"{resource.resource_id}: {e}"
                )

        return {
            "synced_resources": synced_resources,
            "total_resources": len(resources)
        }

    def close(self):
        self.graph.close()
