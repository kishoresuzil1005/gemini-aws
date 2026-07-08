from typing import List, Any

class SourceAttribution:
    def __init__(self):
        pass

    def attribute(self, target_resource: str, tool_responses: List[Any]) -> List[str]:
        """
        Tracks which analyzers and data sources contributed to the answer.
        """
        sources = []
        if target_resource:
            sources.append("Neo4j Knowledge Graph")
            
        for tr in tool_responses:
            sources.append(tr.tool_name)
            
        return sources
