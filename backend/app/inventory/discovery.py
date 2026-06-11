from sqlalchemy.orm import Session
from app.database import ResourceDB, CloudAccountDB, ResourceNodeDB, ResourceEdgeDB
from app.services.discovery.scanner import AWSDiscoveryScanner


def discover_resources(
    db: Session,
    cloud_account_id: int
):
    account = (
        db.query(CloudAccountDB)
        .filter(
            CloudAccountDB.id == cloud_account_id
        )
        .first()
    )

    if not account:
        return

    resources = []

    if account.provider == "AWS":

        try:

            discovered = AWSDiscoveryScanner.scan_all(
                region=account.region
            )

            if not discovered:
                raise Exception(
                    "No AWS resources discovered"
                )

            for r in discovered:

                resources.append(
                    ResourceDB(
                        cloud_account_id=
                        cloud_account_id,

                        provider=r.get(
                            "provider",
                            "AWS"
                        ),

                        resource_type=r.get(
                            "type"
                        ),

                        resource_id=r.get(
                            "id"
                        ),

                        name=r.get(
                            "name"
                        ),

                        region=r.get(
                            "region",
                            account.region
                        ),

                        status=(
                            r.get("status")
                            or r.get("state")
                        ),

                        instance_type=r.get(
                            "instance_type"
                        ),

                        instance_class=r.get(
                            "instance_class"
                        ),

                        size_gb=r.get(
                            "size_gb"
                        ),

                        memory_size=r.get(
                            "memory_size"
                        ),

                        monthly_requests=r.get(
                            "monthly_requests"
                        ),

                        avg_duration_ms=r.get(
                            "avg_duration_ms"
                        )
                    )
                )

        except Exception as e:

            raise Exception(
                f"AWS discovery failed: {e}"
            )

    else:

        raise Exception(
            f"Provider {account.provider} not supported"
        )

    db.query(ResourceDB).filter(
        ResourceDB.cloud_account_id ==
        cloud_account_id
    ).delete()
    
    # Also clear nodes and edges
    db.query(ResourceNodeDB).delete()
    db.query(ResourceEdgeDB).delete()

    db.add_all(resources)

    nodes = []
    edges = []
    for r in discovered:
        # Avoid creating duplicate nodes (e.g. EC2 instance discovered twice in different regions somehow, just in case)
        nodes.append(ResourceNodeDB(
            resource_id=r.get("id"),
            resource_type=r.get("type"),
            name=r.get("name"),
            provider=r.get("provider", "AWS")
        ))
        for dep in r.get("dependencies", []):
            edges.append(ResourceEdgeDB(
                source_id=r.get("id"),
                target_id=dep.get("id"),
                relationship="depends_on"
            ))
            # Also add the target node if it doesn't exist? Well, since nodes has unique constraint, we'll wait and commit at the end, handling unique constraint by merging. Actually it's easier to just upsert or handle them manually.
            # But the prompt says "Store: ResourceNode, ResourceEdge". I will add target nodes to nodes list if we want to show them? Actually, the prompt says for Level 3: "returns dependencies [{type, name}]", which can be queried from ResourceEdgeDB and ResourceNodeDB. Wait, if the target is just a VPC or Subnet, maybe we don't have its record in `ResourceNodeDB`? We can create a dummy node.
            nodes.append(ResourceNodeDB(
                resource_id=dep.get("id"),
                resource_type=dep.get("type"),
                name=dep.get("name") or dep.get("id"),
                provider="AWS"
            ))

    # Add nodes directly with ignoring duplicates
    # Since we might have duplicates in the nodes list, let's filter them out by resource_id
    unique_nodes = {}
    for n in nodes:
        if n.resource_id not in unique_nodes:
            unique_nodes[n.resource_id] = n
    
    db.add_all(unique_nodes.values())
    db.add_all(edges)

    db.commit()