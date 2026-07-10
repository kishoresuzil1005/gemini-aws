from typing import Dict, Optional

class ResourceParser:
    """Parses Kubernetes resource URIs."""
    
    @staticmethod
    def parse(resource_uri: str) -> Dict[str, Optional[str]]:
        """
        Parses formats like: namespaces/default/pods/my-pod
        or just: default/my-pod
        """
        parts = resource_uri.strip("/").split("/")
        parsed = {
            "namespace": "default",
            "resource_type": None,
            "resource_name": None
        }
        
        if "namespaces" in parts:
            idx = parts.index("namespaces")
            if idx + 1 < len(parts):
                parsed["namespace"] = parts[idx+1]
                if idx + 2 < len(parts):
                    parsed["resource_type"] = parts[idx+2]
                if idx + 3 < len(parts):
                    parsed["resource_name"] = parts[idx+3]
        elif len(parts) == 2:
            parsed["namespace"] = parts[0]
            parsed["resource_name"] = parts[1]
        elif len(parts) == 1:
            parsed["resource_name"] = parts[0]
            
        return parsed
