from sqlalchemy.orm import Session
from app.models import ResourceDB, CloudAccountDB, ScanHistoryDB
from app.services.discovery.scanner import AWSDiscoveryScanner
from app.services.discovery.normalizer import ResourceNormalizer
from datetime import datetime

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

    if account.provider == "AWS":
        try:
            # 1. Discover AWS
            scan_result = AWSDiscoveryScanner.scan_all(region=region)
            
            # 2. Normalize
            normalized_resources = ResourceNormalizer.normalize(scan_result.resources)
            scan_result.account_id = str(cloud_account_id)

            # 3. Save Inventory
            for norm in normalized_resources:
                # Upsert logic based on resource_id
                existing = db.query(ResourceDB).filter(ResourceDB.resource_id == norm["resource_id"]).first()
                if existing:
                    existing.name = norm["name"]
                    existing.region = norm["region"]
                    existing.status = norm["status"]
                    existing.resource_metadata = norm["metadata"]
                    existing.scan_id = scan_result.scan_id
                    existing.resource_version += 1
                else:
                    db.add(ResourceDB(
                        cloud_account_id=cloud_account_id,
                        provider=norm["provider"],
                        resource_type=norm["resource_type"],
                        resource_id=norm["resource_id"],
                        name=norm["name"],
                        region=norm["region"],
                        status=norm["status"],
                        resource_metadata=norm["metadata"],
                        scan_id=scan_result.scan_id,
                        resource_version=1
                    ))

            # 4. Save Scan History
            db.add(ScanHistoryDB(
                id=scan_result.scan_id,
                account_id=str(cloud_account_id),
                scan_start=scan_result.started_at,
                scan_end=scan_result.finished_at,
                status="COMPLETED",
                resources_found=len(normalized_resources),
                duration=scan_result.duration,
                errors=len(scan_result.errors),
                warnings=len(scan_result.warnings)
            ))

            db.commit()

            # Phase 4 removes Neo4j syncing from here; GraphSyncService handles it offline
            return scan_result

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
        print("STEP 1")
        
        #
        # Build AWS relationships dynamically
        #

        print("STEP 2")
        builder = AWSRelationshipBuilder()
        print("STEP 3")

        relationships_new = builder.build()
        print("STEP 4", len(relationships_new))

        print("===================================")
        print("builder.build() finished")
        print("relationships:", len(relationships_new))

        for r in relationships_new[:10]:
            print(r)

        print("===================================")

        print(f"[Discovery] Writing {len(relationships_new)} relationships to Neo4j")

        print("STEP 5")
        for rel in relationships_new:

            try:

                print("[REL]", rel)

                Neo4jService.create_resource({
                    "id": rel["from"],
                    "type": rel.get("source_type", "Resource"),
                    "name": rel["from"]
                })

                Neo4jService.create_resource({
                    "id": rel["to"],
                    "type": rel.get("target_type", "Resource"),
                    "name": rel["to"]
                })

                Neo4jService.create_relationship(
                    source_id=rel["from"],
                    target_id=rel["to"],
                    relationship_type=rel["type"]
                )

                print(
                    "[CREATED]",
                    rel["from"],
                    rel["type"],
                    rel["to"]
                )

            except Exception as e:

                print(
                    "[Neo4j Relationship Error]",
                    rel,
                    str(e)
                )

        print("STEP 6")
    except Exception as e:
        db.rollback()
        raise Exception(
            f"Database commit failed: {e}"
        )