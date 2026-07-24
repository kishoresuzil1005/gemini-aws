# knowledge/service/knowledge_health.py
"""Health checks across the Knowledge Platform."""

from typing import Dict, Any

class KnowledgeHealth:
    def __init__(self, resource_cat, rel_cat, rule_cat, graph):
        self.catalogs = {
            "resources": resource_cat,
            "relationships": rel_cat,
            "rules": rule_cat,
            "graph": graph
        }

    def check(self) -> Dict[str, Any]:
        """Polls all subcomponents to ensure they are loaded and active."""
        status = {"status": "HEALTHY", "components": {}}
        
        try:
            # We assume each component exposes a version_manager property
            for name, component in self.catalogs.items():
                if component:
                    status["components"][name] = {
                        "status": "UP",
                        "version": component.version_manager.current_version
                    }
                else:
                    status["components"][name] = {"status": "DOWN"}
                    status["status"] = "DEGRADED"
        except Exception as e:
            status["status"] = "UNHEALTHY"
            status["error"] = str(e)
            
        return status
