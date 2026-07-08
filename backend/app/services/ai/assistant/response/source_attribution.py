from typing import List, Any

class SourceAttribution:
    def __init__(self):
        pass

    def attribute(self, target_resource: str, tool_responses: List[Any]) -> List[Any]:
        """
        Tracks which analyzers and data sources contributed to the answer.
        """
        sources = []
        if target_resource:
            sources.append("Neo4j Knowledge Graph")
            
        for tr in tool_responses:
            if isinstance(tr.context, dict) and "sources" in tr.context:
                # Extend with detailed source objects
                sources.extend(tr.context["sources"])
            else:
                sources.append(tr.tool_name)
            
        return sources
