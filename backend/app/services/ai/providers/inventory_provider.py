from typing import Dict, Any

class InventoryProvider:
    def get_context(self, resource_id: str) -> Dict[str, Any]:
        return {"source": "PostgreSQL", "data": "inventory context for " + str(resource_id)}
