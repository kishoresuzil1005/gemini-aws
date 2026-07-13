from app.services.ai.assistant.knowledge_graph.core.graph_repository import GraphRepository

class GraphExporter:
    """Exports graph to Neo4j, GraphML, JSON, CSV, Mermaid."""
    
    def export_to_mermaid(self, repository: GraphRepository) -> str:
        graph = repository.engine.get_underlying_graph()
        lines = ["graph TD;"]
        for u, v in graph.edges():
            lines.append(f"    {u}-->{v};")
        return "\n".join(lines)