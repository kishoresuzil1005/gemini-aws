from sqlalchemy.orm import Session
from app.database import ResourceDB, CloudAccountDB, ResourceNodeDB, ResourceEdgeDB, ResourceRelationshipDB
from app.services.discovery.scanner import AWSDiscoveryScanner
from app.providers.aws.regions import get_all_regions
from app.services.graph.neo4j_service import Neo4jService
from app.services.graph.aws_relationship_builder import AWSRelationshipBuilder


def discover_resources(
    db: Session,
    cloud_account_id: int,
    region: str | None = None
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

            if region and region.lower() != "all":
                regions_to_scan = [region]
            else:
                regions_to_scan = get_all_regions()

            print(
                f"[DISCOVERY] Regions discovered: "
                f"{len(regions_to_scan)}"
            )

            print(regions_to_scan)

            discovered = []

            seen_global_ids = set()

            for r_name in regions_to_scan:

                scan_res = AWSDiscoveryScanner.scan_all(
                    region=r_name
                )

                for item in scan_res:

                    if item.get("region") == "global":

                        if item.get("id") not in seen_global_ids:

                            seen_global_ids.add(
                                item.get("id")
                            )

                            discovered.append(item)

                    else:

                        discovered.append(item)

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

    # --------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------
    if not discovered:
        raise Exception(
            "Discovery returned zero resources. "
            "Aborting database update."
        )

    print(
        f"[DISCOVERY] Validation passed. "
        f"Resources found: {len(discovered)}"
    )

    # --------------------------------------------------
    # DELETE OLD DATA ONLY AFTER
    # SUCCESSFUL DISCOVERY
    # --------------------------------------------------
    db.query(ResourceDB).filter(
        ResourceDB.cloud_account_id ==
        cloud_account_id
    ).delete()

    # Also clear nodes, edges, and relationships
    db.query(ResourceNodeDB).delete()
    db.query(ResourceEdgeDB).delete()
    db.query(ResourceRelationshipDB).delete()

    print(
        "[DISCOVERY] Old inventory removed"
    )
    
    # Reset/clear Neo4j database graph
    try:
        Neo4jService.clear_graph()
    except Exception as ne_e:
        print(f"Failed to clear Neo4j graph during discovery: {ne_e}")

    db.add_all(resources)

    nodes = []
    edges = []
    relationships = []
    for r in discovered:
        # Avoid creating duplicate nodes (e.g. EC2 instance discovered twice in different regions somehow, just in case)
        nodes.append(ResourceNodeDB(
            resource_id=r.get("id"),
            resource_type=r.get("type"),
            name=r.get("name"),
            provider=r.get("provider", "AWS")
        ))
        
        # Merge source node in Neo4j
        try:
            Neo4jService.create_resource({
                "id": r.get("id"),
                "type": r.get("type"),
                "name": r.get("name"),
                "region": r.get("region"),
                "status": r.get("status") or r.get("state")
            })
        except Exception as ne_e:
            print(f"Failed to merge source state to Neo4j: {ne_e}")

        for dep in r.get("dependencies", []):
            dep_type = dep.get("type", "").upper()
            rel_type = "DEPENDS_ON"
            if dep_type == "VPC":
                rel_type = "IN_VPC"
            elif dep_type == "SUBNET":
                rel_type = "IN_SUBNET"
            elif dep_type in ("SECURITYGROUP", "SECURITY_GROUP"):
                rel_type = "USES_SG"
            elif dep_type == "EBS":
                rel_type = "ATTACHED_TO"
            elif dep_type in ("IAM", "IAM_ROLE", "IAM_USER"):
                rel_type = "USES_ROLE"

            edges.append(ResourceEdgeDB(
                source_id=r.get("id"),
                target_id=dep.get("id"),
                relationship=rel_type.lower()
            ))
            relationships.append(ResourceRelationshipDB(
                source_resource_id=r.get("id"),
                target_resource_id=dep.get("id"),
                relationship_type=rel_type
            ))
            # Also add the target node if it doesn't exist
            nodes.append(ResourceNodeDB(
                resource_id=dep.get("id"),
                resource_type=dep.get("type"),
                name=dep.get("name") or dep.get("id"),
                provider="AWS"
            ))

            # Merge target node and relation in Neo4j
            try:
                Neo4jService.create_resource({
                    "id": dep.get("id"),
                    "type": dep.get("type"),
                    "name": dep.get("name") or dep.get("id"),
                    "region": "global",
                    "status": "active"
                })
                Neo4jService.create_relationship(
                    source_id=r.get("id"),
                    target_id=dep.get("id"),
                    relationship_type=rel_type
                )
            except Exception as ne_e:
                print(f"Failed to merge target/relation to Neo4j: {ne_e}")

    # Add nodes directly with ignoring duplicates
    # Since we might have duplicates in the nodes list, let's filter them out by resource_id
    unique_nodes = {}
    for n in nodes:
        if n.resource_id not in unique_nodes:
            unique_nodes[n.resource_id] = n
    
    db.add_all(unique_nodes.values())
    db.add_all(edges)
    db.add_all(relationships)

    # Priority 1 Direct IGW Discovery fallback
    import boto3
    try:
        ec2 = boto3.client("ec2", region_name=region if region and region.lower() != "all" else "us-east-1")
        response = ec2.describe_internet_gateways()
        for igw in response.get("InternetGateways", []):
            igw_id = igw.get("InternetGatewayId")
            if igw_id and igw_id not in unique_nodes:
                resource = ResourceNodeDB(
                    resource_id=igw_id,
                    resource_type="InternetGateway",
                    name=igw_id,
                    provider="AWS"
                )
                db.add(resource)
    except Exception as e:
        print(f"Failed direct IGW fallback discovery: {e}")

    try:
        db.commit()
        print(
            "[DISCOVERY] Database commit successful"
        )
        
        #
        # Build AWS relationships dynamically
        #

        builder = AWSRelationshipBuilder()

        relationships_new = builder.build()

        print(f"[Discovery] Writing {len(relationships_new)} relationships to Neo4j")

        for rel in relationships_new:

            try:

                Neo4jService.create_relationship(
                    source_id=rel["from"],
                    target_id=rel["to"],
                    relationship_type=rel["type"]
                )

            except Exception as e:

                print(
                    "[Neo4j Relationship Error]",
                    rel,
                    str(e)
                )
    except Exception as e:
        db.rollback()
        raise Exception(
            f"Database commit failed: {e}"
        )