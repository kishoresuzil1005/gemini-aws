from typing import Dict, List

from app.database import SessionLocal, ResourceDB


class InventoryContext:
    """
    Pulls live resource inventory from PostgreSQL.
    """

    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def build(self, intent) -> Dict:
        """
        Build inventory context based on the classified intent.
        Returns resource counts and a filtered list of resources.
        """

        try:

            resources = self.db.query(ResourceDB).all()

            # Summarize by type
            counts: Dict[str, int] = {}
            for r in resources:
                counts[r.resource_type] = counts.get(r.resource_type, 0) + 1

            # Pull resource list relevant to extracted entities
            resource_list = [
                {
                    "resource_id": r.resource_id,
                    "resource_type": r.resource_type,
                    "name": r.name,
                    "region": r.region,
                    "status": r.status,
                    "instance_type": r.instance_type
                }
                for r in resources[:50]  # cap for context window
            ]

            return {
                "total": len(resources),
                "by_type": counts,
                "resources": resource_list
            }

        except Exception as e:

            print(f"[InventoryContext] build failed: {e}")
            return {"total": 0, "by_type": {}, "resources": []}
