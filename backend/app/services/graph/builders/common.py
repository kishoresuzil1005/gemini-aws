from typing import List, Dict, Any, Optional
from app.models import ResourceDB

class GraphMetadataHelper:
    """Helper to safely extract metadata directly from ResourceDB JSONB column."""
    
    @staticmethod
    def get_configuration(resource: ResourceDB) -> Dict[str, Any]:
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})

    @staticmethod
    def get_security(resource: ResourceDB) -> Dict[str, Any]:
        metadata = resource.resource_metadata or {}
        return metadata.get("security", {})
        
    @staticmethod
    def get_tags(resource: ResourceDB) -> Dict[str, Any]:
        metadata = resource.resource_metadata or {}
        return metadata.get("tags", {})
        
    @staticmethod
    def get_metadata(resource: ResourceDB) -> Dict[str, Any]:
        metadata = resource.resource_metadata or {}
        return metadata.get("metadata", {})

class GraphRelationship:
    """Helper to consistently build edge dictionaries."""
    
    @staticmethod
    def create(source: str, target: str, relationship: str, source_type: str, target_type: str) -> Optional[Dict[str, Any]]:
        if not source or not target:
            return None
        return {
            "from": source,
            "to": target,
            "type": relationship,
            "source_type": source_type,
            "target_type": target_type
        }

class GraphBuilderHelper:
    """Legacy helper for builders not yet migrated to V2."""
    @staticmethod
    def build_edges(resource: ResourceDB, resource_lookup: Dict[str, str]) -> List[Dict[str, Any]]:
        edges = []
        metadata = resource.resource_metadata or {}
        for dep in metadata.get("dependencies", []):
            target_id = dep.get("id")
            if target_id in resource_lookup:
                edges.append({
                    "from": resource.resource_id,
                    "to": target_id,
                    "type": "DEPENDS_ON", # generic fallback
                    "source_type": resource.resource_type,
                    "target_type": resource_lookup[target_id]
                })
        return edge