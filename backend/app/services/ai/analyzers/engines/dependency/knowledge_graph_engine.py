"""
Knowledge Graph Engine.
Enriches raw topologies with domain concepts (e.g. Application Groups, Shared Infrastructure).
"""
from typing import Dict, Any, List

class KnowledgeGraphEngine:
    
    @classmethod
    def enrich(cls, infra_graph: Any, graph_index: Any) -> Dict[str, Any]:
        """
        Topological clustering to identify shared infrastructure and application groups.
        """
        knowledge = {
            "application_groups": {},
            "shared_infrastructure": [],
            "shared_databases": [],
            "shared_iam_roles": [],
            "shared_security_groups": []
        }
        
        for node_id, props in infra_graph.nodes.items():
            node_type = str(props.get("type", props.get("resource_type", ""))).lower()
            
            # Application Groups (by Tag)
            app_tag = props.get("tags", {}).get("Application", props.get("tags", {}).get("application"))
            if app_tag:
                if app_tag not in knowledge["application_groups"]:
                    knowledge["application_groups"][app_tag] = []
                knowledge["application_groups"][app_tag].append(node_id)
                
            # Shared Infrastructure (High Fan-in)
            fan_in = len(graph_index.reverse_adjacency.get(node_id, set()))
            if fan_in > 5:
                if "db" in node_type or "rds" in node_type or "dynamodb" in node_type:
                    knowledge["shared_databases"].append(node_id)
                elif "iam" in node_type or "role" in node_type:
                    knowledge["shared_iam_roles"].append(node_id)
                elif "securitygroup" in node_type or "sg" in node_type:
                    knowledge["shared_security_groups"].append(node_id)
                else:
                    knowledge["shared_infrastructure"].append(node_id)
                    
        return knowledge
