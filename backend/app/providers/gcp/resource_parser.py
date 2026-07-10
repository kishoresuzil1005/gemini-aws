from typing import Dict, Optional

class ResourceParser:
    """Parses complex GCP resource URIs into parts."""
    
    @staticmethod
    def parse(resource_uri: str) -> Dict[str, Optional[str]]:
        """
        Parses uris like: projects/demo/zones/us-central1-a/instances/vm01
        """
        parts = resource_uri.strip("/").split("/")
        parsed = {
            "project": None,
            "zone": None,
            "region": None,
            "resource_type": None,
            "resource_name": None
        }
        
        i = 0
        while i < len(parts):
            key = parts[i]
            if i + 1 < len(parts):
                val = parts[i+1]
                if key == "projects":
                    parsed["project"] = val
                elif key == "zones":
                    parsed["zone"] = val
                elif key == "regions":
                    parsed["region"] = val
                else:
                    parsed["resource_type"] = key
                    parsed["resource_name"] = val
            i += 2
            
        return parsed
