from typing import Dict, Any, Optional

class GraphRelationship:
    """Factory for creating consistent relationship edge dictionaries."""
    
    @staticmethod
    def create(source: str, target: str, relationship: str, source_type: str, target_type: str) -> Optional[Dict[str, Any]]:
        """
        Builds a standard edge dictionary.
        Returns None if source or target are missing.
        """
        if not source or not target:
            return None
            
        return {
            "from": source,
            "to": target,
            "type": relationship,
            "source_type": source_type,
            "target_type": target_type
        }