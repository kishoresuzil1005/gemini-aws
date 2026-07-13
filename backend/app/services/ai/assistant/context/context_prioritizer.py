from typing import Dict, Any, List

class ContextPrioritizer:
    def __init__(self):
        # Priority mapping: lower number means higher priority (appears first)
        self.priority_map = {
            "RESOURCE": 1,
            "SECURITY": 2,
            "RECOMMENDATION": 3,
            "DEPENDENCIES": 4,
            "BLAST_RADIUS": 5,
            "COST": 6,
            "METADATA": 7,
            "INVENTORY": 8
        }

    def prioritize_sections(self, sections: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Sorts the context sections based on their priority.
        sections should be a list of dicts: {"title": "SECURITY", "content": "..."}
        """
        def get_priority(section):
            # Try to match the title to our priority map
            title = section.get("title", "").upper()
            for key, priority in self.priority_map.items():
                if key in title:
                    return priority
            return 99 # Default low priority
            
        return sorted(sections, key=get_priority)