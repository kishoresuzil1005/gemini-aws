from typing import Dict, List

from sqlalchemy.orm import Session

from app.database import SessionLocal, ResourceDB


class InventoryContext:

    def __init__(self):
        self.db: Session = SessionLocal()

    def close(self):
        self.db.close()

    def build(self, intent) -> List[Dict]:

        try:

            query = self.db.query(ResourceDB)

            # Filter by service types if intent carries them
            if hasattr(intent, "resources") and intent.resources:
                services = [
                    r.resource_type.value
                    for r in intent.resources
                    if r.resource_type
                ]
                if services:
                    query = query.filter(
                        ResourceDB.resource_type.in_(services)
                    )

            resources = query.limit(100).all()

            return [
                {
                    "id": r.id,
                    "name": r.name,
                    "resource_type": r.resource_type,
                    "resource_id": r.resource_id,
                    "region": r.region,
                    "status": r.status,
                    "cloud_account_id": r.cloud_account_id,
                    "instance_type": r.instance_type,
                    "tags": r.tags,
                }
                for r in resources
            ]

        except Exception as e:

            print(f"[InventoryContext] build failed: {e}")
            return []
