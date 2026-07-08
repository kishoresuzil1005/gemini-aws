from typing import Dict, Any
from app.models import ResourceDB

class GraphMetadataHelper:
    """Helper to safely extract domain-specific metadata from ResourceDB JSONB column."""
    
    @staticmethod
    def get_network(resource: ResourceDB) -> Dict[str, Any]:
        """Returns network-related configuration like vpc_id, subnet_id, enis."""
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})

    @staticmethod
    def get_security(resource: ResourceDB) -> Dict[str, Any]:
        """Returns security-related configuration like security_groups, iam roles, kms keys."""
        metadata = resource.resource_metadata or {}
        return metadata.get("security", {})
        
    @staticmethod
    def get_storage(resource: ResourceDB) -> Dict[str, Any]:
        """Returns storage-related configuration like ebs_volumes."""
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})

    @staticmethod
    def get_compute(resource: ResourceDB) -> Dict[str, Any]:
        """Returns compute-related configurations."""
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})

    @staticmethod
    def get_database(resource: ResourceDB) -> Dict[str, Any]:
        """Returns database-related configurations."""
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})
        
    @staticmethod
    def get_tags(resource: ResourceDB) -> Dict[str, Any]:
        """Returns AWS tags."""
        metadata = resource.resource_metadata or {}
        return metadata.get("tags", {})
        
    @staticmethod
    def get_configuration(resource: ResourceDB) -> Dict[str, Any]:
        """Returns general configurations."""
        metadata = resource.resource_metadata or {}
        return metadata.get("configuration", {})
