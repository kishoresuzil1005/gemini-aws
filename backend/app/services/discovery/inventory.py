from sqlalchemy.orm import Session
from app.models import ResourceDB, CloudAccountDB
from typing import List, Dict, Any

class InventoryManager:
    @staticmethod
    def sync_inventory(db: Session, cloud_account_id: int, discovered_resources: List[Dict[str, Any]]) -> List[ResourceDB]:
        """
        Clears previous entries and populates the database with newly scanned resources.
        Coordinates live inventory storage in PostgreSQL (Phase 2).
        """
        account = db.query(CloudAccountDB).filter(CloudAccountDB.id == cloud_account_id).first()
        if not account:
            return []

        # Map to database models
        db_resources = []
        for r in discovered_resources:
            db_resources.append(ResourceDB(
                cloud_account_id=cloud_account_id,
                provider=account.provider,
                resource_type=r["type"],
                resource_id=r["id"],
                name=r["name"],
                region=r["region"],
                status=r["status"]
            ))

        # Atomic transaction: delete old resource definitions for this distinct account and overwrite
        db.query(ResourceDB).filter(ResourceDB.cloud_account_id == cloud_account_id).delete()
        
        if db_resources:
            db.add_all(db_resources)
            db.commit()
            
        return db_resources
