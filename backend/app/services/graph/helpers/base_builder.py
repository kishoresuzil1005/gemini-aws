from typing import List, Dict, Any
from app.models import ResourceDB

class BaseGraphBuilder:
    """Base interface for all AWS graph builders."""
    
    @staticmethod
    def build(resources: List[ResourceDB]) -> List[Dict[str, Any]]:
        """
        Parses resources and returns a list of relationship edges.
        Must be implemented by every graph builder.
        """
        raise NotImplementedError("Each graph builder must implement the build() method.")
