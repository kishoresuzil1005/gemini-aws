from collections import defaultdict
from app.database import ResourceDB
from app.services.topology.category_map import CATEGORY_MAP

class TopologyService:
    def __init__(self, db):
        self.db = db

    def get_categories(self):
        resources = self.db.query(ResourceDB).all()
        counts = defaultdict(int)

        # Pre-initialize core categories to guarantee they are displayed
        default_categories = ["Compute", "Storage", "Database", "Network", "Security"]
        for cat in default_categories:
            counts[cat] = 0

        for r in resources:
            r_type_upper = (r.resource_type or "").upper()
            category = CATEGORY_MAP.get(r_type_upper, "Other")
            counts[category] += 1

        return [
            {
                "name": category,
                "count": count
            }
            for category, count in counts.items()
            if category != "Other" or count > 0
        ]

    def get_resources_by_category(self, category: str):
        resources = self.db.query(ResourceDB).all()
        result = []

        for r in resources:
            r_type_upper = (r.resource_type or "").upper()
            mapped = CATEGORY_MAP.get(r_type_upper, "Other")

            if mapped.lower() == category.lower():
                result.append({
                    "id": r.resource_id,
                    "type": r.resource_type,
                    "name": r.name or r.resource_id,
                    "region": r.region or "unknown",
                    "status": r.status or "unknown"
                })

        result.sort(key=lambda x: (x["type"], x["name"]))
        return result
