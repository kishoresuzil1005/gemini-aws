from sqlalchemy.orm import Session

from app.database import ResourceDB
from app.services.graph.neo4j_service import Neo4jService


class GraphSyncService:

    def __init__(self, db: Session):
        self.db = db
        self.graph = Neo4jService()

    def sync_resources(self):

        resources = self.db.query(ResourceDB).all()

        synced = 0
        failed = 0

        for resource in resources:

            try:

                if not resource.resource_id:
                    failed += 1
                    continue

                self.graph.create_node(
                    node_type=resource.resource_type,
                    resource_id=resource.resource_id,
                    name=resource.name or resource.resource_id,
                    provider=resource.provider
                )

                synced += 1

            except Exception as e:

                print(
                    f"[GRAPH_SYNC] "
                    f"{resource.resource_id}: {e}"
                )

                failed += 1

        total = len(resources)

        success_rate = 0

        if total > 0:
            success_rate = round(
                (synced / total) * 100,
                2
            )

        # Build and sync relationships (Phase 1.6)
        try:
            from app.services.graph.aws_relationship_builder import AWSRelationshipBuilder
            builder = AWSRelationshipBuilder()
            relationships = builder.build()

            for rel in relationships:
                # Pre-create standard nodes to ensure MATCH does not fail in sandbox
                try:
                    self.graph.create_node(
                        node_type="Resource",
                        resource_id=rel["from"],
                        name=rel["from"]
                    )
                    self.graph.create_node(
                        node_type="Resource",
                        resource_id=rel["to"],
                        name=rel["to"]
                    )
                except Exception:
                    pass

                # Store fallback edges (this is where in-memory counts are collected)
                from app.services.graph.neo4j_service import MemoryGraphStore
                MemoryGraphStore.merge_edge(rel["from"], rel["to"], rel["type"])

                if self.graph.driver:
                    try:
                        query = """
                        MATCH (a {id:$from_id})
                        MATCH (b {id:$to_id})

                        MERGE (a)-[r:%s]->(b)
                        """ % rel["type"]
                        with self.graph.driver.session() as session:
                            session.run(query, from_id=rel["from"], to_id=rel["to"])
                    except Exception as re_e:
                        print(f"Failed to merge relationship ({rel['from']})-[{rel['type']}]->({rel['to']}) in Neo4j: {re_e}")
        except Exception as ge_e:
            print(f"Error executing graph relationships builder: {ge_e}")

        from app.services.graph.sync_tracker import SyncTracker
        SyncTracker.update()

        return {
            "total_resources": total,
            "synced_resources": synced,
            "failed_resources": failed,
            "success_rate": success_rate
        }

    def close(self):
        self.graph.close()
