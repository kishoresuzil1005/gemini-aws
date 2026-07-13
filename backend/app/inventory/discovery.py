import uuid
from sqlalchemy.orm import Session
from app.models import ResourceDB, CloudAccountDB, ScanHistoryDB, ResourceRelationshipDB
from app.services.discovery.scanner import AWSDiscoveryScanner
from app.services.discovery.normalizer import ResourceNormalizer
from datetime import datetime

def discover_resources(
    db: Session,
    cloud_account_id: int,
    region: str | None = None
):
    print("=" * 80)
    print("HELLO FROM DISCOVERY")
    print("cloud_account_id =", cloud_account_id)
    print("region =", region)
    print("=" * 80)
    
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
            print("BEFORE SCANNER")
            scan_result = AWSDiscoveryScanner.scan_all(region=region)
            print("POINT 2")
            
            print("=" * 80)
            print("SCAN RESULT")
            print("scan_id =", scan_result.scan_id)
            print("resources =", len(scan_result.resources))
            print("=" * 80)
            
            # 2. Normalize
            normalized_resources = ResourceNormalizer.normalize(scan_result.resources)
            
            print("POINT 3")
            
            print("=" * 80)
            print("NORMALIZED =", len(normalized_resources))
            if normalized_resources:
                print(normalized_resources[0])
            print("=" * 80)
            
            scan_result.account_id = str(cloud_account_id)

            # 3. Save Inventory
            print("POINT 4 - Saving inventory")
            for norm in normalized_resources:
                print("Saving:", norm["resource_id"])
                print("Metadata:", norm.get("metadata"))
                print("Scan:", scan_result.scan_id)
                
                existing = db.query(ResourceDB).filter(ResourceDB.resource_id == norm["resource_id"]).first()
                if existing:
                    existing.name = norm["name"]
                    existing.region = norm["region"]
                    existing.status = norm["status"]
                    existing.resource_metadata = {
                        **dict(norm.get("metadata", {})),
                        **dict(norm.get("configuration", {})),
                        **dict(norm.get("security", {})),
                    }
                    existing.scan_id = uuid.UUID(scan_result.scan_id)
                    existing.resource_version = (existing.resource_version or 0) + 1
                else:
                    db.add(ResourceDB(
                        cloud_account_id=cloud_account_id,
                        provider=norm["provider"],
                        resource_type=norm["resource_type"],
                        resource_id=norm["resource_id"],
                        name=norm["name"],
                        region=norm["region"],
                        status=norm["status"],
                        resource_metadata={
                            **dict(norm.get("metadata", {})),
                            **dict(norm.get("configuration", {})),
                            **dict(norm.get("security", {})),
                        },
                        scan_id=uuid.UUID(scan_result.scan_id),
                        resource_version=1
                    ))

            # 4. Save Scan History
            print("POINT 5 - Saving scan history")
            db.add(ScanHistoryDB(
                id=uuid.UUID(scan_result.scan_id),
                account_id=str(cloud_account_id),
                scan_start=scan_result.started_at,
                scan_end=scan_result.finished_at,
                status="COMPLETED",
                resources_found=len(normalized_resources),
                duration=scan_result.duration,
                errors=len(scan_result.errors),
                warnings=len(scan_result.warnings)
            ))

            # 5. Save Dependencies to PostgreSQL
            print("POINT 6 - Saving relationships")
            relationships = []
            for norm in normalized_resources:
                source_id = norm["resource_id"]
                for dep in norm.get("dependencies", []):
                    rel_type = "DEPENDS_ON"
                    dep_type = dep.get("type", "").upper()
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
                        
                    relationships.append(ResourceRelationshipDB(
                        source_resource_id=source_id,
                        target_resource_id=dep["id"],
                        relationship_type=rel_type
                    ))

            all_resource_ids = [r["resource_id"] for r in normalized_resources]
            if all_resource_ids:
                db.query(ResourceRelationshipDB).filter(ResourceRelationshipDB.source_resource_id.in_(all_resource_ids)).delete(synchronize_session=False)
            
            db.add_all(relationships)

            print("POINT 7 - COMMIT")
            for norm in normalized_resources:
                for field in [
                    "provider",
                    "resource_type",
                    "resource_id",
                    "region",
                    "status",
                    "instance_type",
                    "instance_class",
                    "name",
                ]:
                    value = str(norm.get(field, ""))
                    if len(value) > 100:
                        print(f"{field} length={len(value)}")
                        print(value)
            
            db.commit()
            print("POINT 8 - DONE")

            # Phase 4 removes Neo4j syncing from here; GraphSyncService handles it offline
            return scan_result

        except Exception as e:
            db.rollback()

            import traceback
            print("=" * 80)
            print("DISCOVERY FAILED")
            traceback.print_exc()
            print("=" * 80)

            raise

    else:
        raise Exception(f"Provider {account.provider} not supported")
