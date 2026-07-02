from typing import Dict, List, Any

from sqlalchemy.orm import Session

from app.database import SessionLocal, ResourceDB


class InventoryContext:

    def __init__(self):
        pass

    def build(self, intent: Any) -> List[Dict]:

        db: Session = SessionLocal()
        
        try:

            query = db.query(ResourceDB)

            services = []
            if isinstance(intent, dict):
                services = intent.get("services", [])
            elif hasattr(intent, "resources") and intent.resources:
                services = [r.resource_type.value for r in intent.resources if r.resource_type]

            if services:
                query = query.filter(
                    ResourceDB.resource_type.in_(services)
                )

            resources = query.limit(100).all()

            return [
                {
                    "id": r.id,
                    "provider": r.provider,
                    "resource_type": r.resource_type,
                    "resource_id": r.resource_id,
                    "name": r.name,
                    "region": r.region,
                    "status": r.status,
                    "instance_type": r.instance_type,
                    "instance_class": r.instance_class,
                    "size_gb": r.size_gb,
                    "memory_size": r.memory_size,
                    "monthly_requests": r.monthly_requests,
                    "avg_duration_ms": r.avg_duration_ms,
                    "tags": r.tags,
                    "discovered_at": r.discovered_at,
                }
                for r in resources
            ]

        finally:
            db.close()
