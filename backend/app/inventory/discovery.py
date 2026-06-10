from sqlalchemy.orm import Session
from app.database import ResourceDB, CloudAccountDB
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

    db.add_all(resources)

    db.commit()