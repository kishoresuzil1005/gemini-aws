from typing import List, Dict, Any

class CitationEngine:
    """
    Enriches every AI response with explicit, traceable citations from the RAG pipeline.
    Prevents hallucination by grounding claims to specific source documents,
    Knowledge Graph nodes, Mission records, and Incident logs.
    
    Builds on top of the existing SourceAttribution in response/source_attribution.py
    by adding structured inline citation formatting.
    """
    SOURCE_TYPE_ICONS = {
        "rag": "📄",
        "knowledge_graph": "🕸️",
        "mission": "🎯",
        "incident": "🔴",
        "cloud_resource": "☁️",
        "learning": "🧠",
    }

    def build_citations(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Converts raw RAG source chunks into numbered citation objects.
        """
        citations = []
        for idx, source in enumerate(sources, start=1):
            source_type = source.get("type", "rag")
            citations.append({
                "ref": f"[{idx}]",
                "icon": self.SOURCE_TYPE_ICONS.get(source_type, "📄"),
                "type": source_type,
                "title": source.get("source", source.get("title", "Unknown")),
                "confidence": round(source.get("score", 0.0), 3),
                "excerpt": source.get("content", "")[:200] + "..." if len(source.get("content", "")) > 200 else source.get("content", "")
            })
        return citations

    def format_citation_block(self, citations: List[Dict[str, Any]]) -> str:
        """
        Generates a markdown citation block appended to AI responses.
        """
        if not citations:
            return ""
        lines = ["\n\n---\n**Sources:**"]
        for c in citations:
            lines.append(f"{c['ref']} {c['icon']} **{c['title']}** (confidence: {c['confidence']})")
        return "\n".join(lines)
