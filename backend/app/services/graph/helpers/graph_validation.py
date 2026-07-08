from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GraphValidation:
    """Pre-build and Post-build relationship validation."""
    
    @staticmethod
    def validate_pre_build(metadata: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validates if metadata has all required fields before attempting to build edges."""
        for field in required_fields:
            if not metadata.get(field):
                return False
        return True
        
    @staticmethod
    def validate_post_build(edges: List[Dict[str, Any]], resource_lookup: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Filters out invalid edges:
        - Removes duplicates
        - Removes edges where target does not exist in inventory
        """
        valid_edges = []
        seen = set()
        
        for edge in edges:
            source = edge.get("from")
            target = edge.get("to")
            rel_type = edge.get("type")
            
            if not source or not target:
                continue
                
            # Check if target exists in our PostgreSQL inventory
            if target not in resource_lookup:
                logger.debug(f"Target node missing: {target}")
                continue
                
            # Check for duplicates
            edge_signature = f"{source}-{rel_type}-{target}"
            if edge_signature in seen:
                continue
                
            seen.add(edge_signature)
            valid_edges.append(edge)
            
        return valid_edges
