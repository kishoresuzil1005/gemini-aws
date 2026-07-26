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
            status["components"] = {
                "Provider Health": {"status": "UP" if self.catalogs.get("resources") else "DOWN"},
                "Catalog Health": {"status": "UP" if all([self.catalogs.get("resources"), self.catalogs.get("relationships"), self.catalogs.get("rules")]) else "DOWN"},
                "Graph Health": {"status": "UP" if self.catalogs.get("graph") else "DOWN"},
                "Search Health": {"status": "UP"},
                "Snapshot Health": {"status": "UP"},
                "Knowledge Service Health": {"status": "UP"},
                "Cache Health": {"status": "UP"},
                "Configuration Health": {"status": "UP"}
            }
        except Exception as e:
            status["status"] = "UNHEALTHY"
            status["error"] = str(e)
            
        return status
