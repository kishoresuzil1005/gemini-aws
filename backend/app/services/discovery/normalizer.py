import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

from datetime import datetime, date

def make_json_safe(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: make_json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [make_json_safe(v) for v in value]
    return value

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
                
                # Capture everything else in metadata
                raw_metadata = raw.get("metadata", {})
                if not isinstance(raw_metadata, dict):
                    raw_metadata = {"_raw_metadata": raw_metadata}
                
                raw_metadata = make_json_safe(raw_metadata)
                    
                norm = {
                    "resource_id": str(resource_id),
                    "resource_type": str(resource_type),
                    "provider": provider,
                    "name": raw.get("name") or str(resource_id),
                    "region": raw.get("region", ""),
                    "status": raw.get("status") or raw.get("state", ""),
                    
                    # Compute specific properties mapped up for querying ease
                    "instance_type": raw.get("instance_type") or raw_metadata.get("instance_type"),
                    "instance_class": raw.get("instance_class") or raw_metadata.get("instance_class"),
                    "size_gb": raw.get("size_gb") or raw_metadata.get("size_gb"),
                    "memory_size": raw.get("memory_size") or raw_metadata.get("memory_size"),
                    "monthly_requests": raw.get("monthly_requests") or raw_metadata.get("monthly_requests"),
                    "avg_duration_ms": raw.get("avg_duration_ms") or raw_metadata.get("avg_duration_ms"),
                    
                    "metadata": raw_metadata.copy(),
                    
                    # Retain dependencies temporarily if GraphBuilder uses them
                    "dependencies": raw.get("dependencies", [])
                }
                
                # Copy remaining keys into metadata, excluding the base keys
                base_keys = {"id", "type", "resource_id", "resource_type", "provider", "name", 
                             "region", "status", "state", "instance_type", "instance_class", 
                             "size_gb", "memory_size", "monthly_requests", "avg_duration_ms", 
                             "dependencies", "metadata", "configuration_hint", "configurationHint"}
                             
                for key, value in raw.items():
                    if key not in base_keys:
                        norm["metadata"][key] = make_json_safe(value)
                
                # If configuration_hint exists, merge it into metadata
                config_hint = raw.get("configuration_hint") or raw.get("configurationHint")
                if config_hint:
                    norm["metadata"]["_legacy_configuration_hint"] = config_hint
                    
                normalized.append(norm)
            except Exception as e:
                logger.error(f"Error normalizing resource {raw}: {e}")
                
        return normalized
