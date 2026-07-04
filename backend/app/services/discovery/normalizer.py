import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ResourceNormalizer:
    @staticmethod
    def normalize(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        
        for raw in resources:
            try:
                # Essential fields
                resource_id = raw.get("resource_id") or raw.get("id")
                resource_type = raw.get("resource_type") or raw.get("type")
                provider = raw.get("provider", "AWS")
                
                if not resource_id or not resource_type:
                    logger.warning(f"Skipping invalid resource: {raw}")
                    continue
                
                # Base normalized object
                norm = {
                    "resource_id": str(resource_id),
                    "resource_type": str(resource_type),
                    "provider": provider,
                    "name": raw.get("name") or str(resource_id),
                    "region": raw.get("region", ""),
                    "status": raw.get("status") or raw.get("state", ""),
                    
                    # Compute specific properties mapped up for querying ease
                    "instance_type": raw.get("instance_type"),
                    "instance_class": raw.get("instance_class"),
                    "size_gb": raw.get("size_gb"),
                    "memory_size": raw.get("memory_size"),
                    "monthly_requests": raw.get("monthly_requests"),
                    "avg_duration_ms": raw.get("avg_duration_ms"),
                    
                    # Capture everything else in metadata
                    "metadata": {},
                    
                    # Retain dependencies temporarily if GraphBuilder uses them (or store in metadata)
                    "dependencies": raw.get("dependencies", [])
                }
                
                # Copy remaining keys into metadata, excluding the base keys
                base_keys = {"id", "type", "resource_id", "resource_type", "provider", "name", 
                             "region", "status", "state", "instance_type", "instance_class", 
                             "size_gb", "memory_size", "monthly_requests", "avg_duration_ms", 
                             "dependencies", "configuration_hint", "configurationHint"}
                             
                for key, value in raw.items():
                    if key not in base_keys:
                        norm["metadata"][key] = value
                
                # If configuration_hint exists, merge it into metadata
                config_hint = raw.get("configuration_hint") or raw.get("configurationHint")
                if config_hint:
                    norm["metadata"]["_legacy_configuration_hint"] = config_hint
                    
                normalized.append(norm)
            except Exception as e:
                logger.error(f"Error normalizing resource {raw}: {e}")
                
        return normalized
