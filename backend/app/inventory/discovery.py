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
