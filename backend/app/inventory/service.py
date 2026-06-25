from sqlalchemy.orm import Session

from app.database import ResourceDB
from app.database import CloudAccountDB

from app.inventory.discovery import discover_resources


def get_all_resources(db: Session):

    return db.query(
        ResourceDB
    ).all()


def get_resources_by_type(
    db: Session,
    resource_type: str
):

    return (
        db.query(ResourceDB)
        .filter(
            ResourceDB.resource_type == resource_type
        )
        .all()
    )


def refresh_inventory(
    db: Session,
    region: str = "all"
):

    account = (
        db.query(CloudAccountDB)
        .first()
    )

    if not account:

        return {
            "success": False,
            "region": region,
            "message": "No cloud account configured"
        }

    try:

        discover_resources(
            db=db,
            cloud_account_id=account.id,
            region=region
        )

        return {
            "success": True,
            "region": region,
            "message": "Inventory refresh completed"
        }

    except Exception as e:

        return {
            "success": False,
            "region": region,
            "message": str(e)
        }
