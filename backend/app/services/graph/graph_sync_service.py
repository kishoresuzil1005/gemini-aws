from sqlalchemy.orm import Session

from app.models import ResourceDB, ResourceNodeDB
from app.services.graph.neo4j_service import Neo4jService


class GraphSyncService:

    def __init__(self, db: Session):
        self.db = db
        self.graph = Neo4jService()

    def sync_resources(self):

        # ── Merge BOTH tables to get all node types ──────────────────────────
        # ResourceDB has EC2, VPC, RDS, S3, Lambda, IAM, EBS ...
        # ResourceNodeDB also has Subnet, SecurityGroup, etc.
        # We merge by resource_id so nothing is missed.

        all_nodes = {}

        # 1. Start with resource_nodes (has Subnet, SecurityGroup)
        try:
            node_rows = self.db.query(ResourceNodeDB).all()
            for row in node_rows:
                if not row.resource_id:
                    continue
                all_nodes[row.resource_id] = {
                    "resource_type": row.resource_type,
                    "resource_id": row.resource_id,
                    "name": row.name or row.resource_id,
                    "provider": row.provider or "AWS"
                }
        except Exception as e:
            print(f"[GRAPH_SYNC] Error reading resource_nodes: {e}")

        # 2. Overlay with resources table (has richer metadata + region)
        try:
            resource_rows = self.db.query(ResourceDB).all()
            for row in resource_rows:
                if not row.resource_id:
                    continue
                all_nodes[row.resource_id] = {
                    "resource_type": row.resource_type,
                    "resource_id": row.resource_id,
                    "name": row.name or row.resource_id,
                    "provider": row.provider or "AWS",
                    "region": row.region or ""
                }
        except Exception as e:
            print(f"[GRAPH_SYNC] Error reading resources: {e}")

        synced = 0
        failed = 0

        for resource_id, data in all_nodes.items():
            try:
                self.graph.create_node(
                    node_type=data["resource_type"],
                    resource_id=data["resource_id"],
                    name=data["name"],
                    provider=data["provider"],
                    region=data.get("region", "")
                )
                synced += 1
            except Exception as e:
                print(f"[GRAPH_SYNC] {resource_id}: {e}")
                failed += 1

        total = len(all_nodes)

        success_rate = 0
        if total > 0:
            success_rate = round((synced / total) * 100, 2)

        # ── Build and sync relationships (Phase 2) ───────────────────────────
        try:
            from app.services.graph.aws_relationship_builder import AWSRelationshipBuilder
            builder = AWSRelationshipBuilder(db=self.db)
            relationships = builder.build()

            for rel in relationships:

                #
                # Ensure source node exists — use real name/region from DB
                # fall back to resource_id only if not found in inventory
                # Merge source
                src_data = all_nodes.get(rel["from"], {})
                self.graph.create_node(
                    node_type=rel.get("source_type", "Resource"),
                    resource_id=rel["from"],
                    name=src_data.get("name") or rel["from"],
                    provider=src_data.get("provider", "AWS"),
                    region=src_data.get("region", "")
                )

                # Merge target
                tgt_data = all_nodes.get(rel["to"], {})
                self.graph.create_node(
                    node_type=rel.get("target_type", "Resource"),
                    resource_id=rel["to"],
                    name=tgt_data.get("name") or rel["to"],
                    provider=tgt_data.get("provider", "AWS"),
                    region=tgt_data.get("region", "")
                )

                #
                # Store in memory
                #

                from app.services.graph.neo4j_service import MemoryGraphStore

                MemoryGraphStore.merge_edge(
                    rel["from"],
                    rel["to"],
                    rel["type"]
                )

                #
                # Write relationship
                #

                self.graph.create_relationship(
                    source_id=rel["from"],
                    target_id=rel["to"],
                    relationship_type=rel["type"]
                )
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
