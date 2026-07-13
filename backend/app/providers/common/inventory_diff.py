from typing import List, Dict, Any, Tuple

class InventoryDiffEngine:
    """
    Calculates differences between existing inventory and new discovery runs.
    Prevents replacing the entire graph/database on each run.
    """
    def calculate_diff(self, old_inventory: List[Dict[str, Any]], new_inventory: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        old_map = {res['resource_id']: res for res in old_inventory if 'resource_id' in res}
        new_map = {res['resource_id']: res for res in new_inventory if 'resource_id' in res}

        added = []
        removed = []
        changed = []

        for r_id, r_data in new_map.items():
            if r_id not in old_map:
                added.append(r_data)
            elif old_map[r_id] != r_data:
                changed.append(r_data)

        for r_id, r_data in old_map.items():
            if r_id not in new_map:
                removed.append(r_data)

        return {
            "added": added,
            "removed": removed,
            "changed": changed
        }
