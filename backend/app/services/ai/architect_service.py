from app.services.graph.criticality_service import CriticalityService
from app.services.graph.graph_analysis_service import GraphAnalysisService
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.ollama_service import OllamaService
from app.services.ai.prompt_builder import PromptBuilder


class ArchitectService:

    def __init__(self):
        self.criticality = CriticalityService()
        self.analysis = GraphAnalysisService()
        self.neo4j = Neo4jService()
        self.ollama = OllamaService()

    def analyze(self, resource_id: str):

        criticality = self.criticality.calculate(resource_id)
        resource_type = self._get_resource_type(resource_id)

        prompt = PromptBuilder.build(
            resource_id,
            resource_type,
            criticality["score"],
            criticality["downstream"],
            criticality["upstream"]
        )

        ai_analysis = self.ollama.generate(
            prompt
        )

        return {
            "resource": resource_id,
            "resource_type": resource_type,
            "risk": criticality["criticality"],
            "criticality_score": criticality["score"],
            "blast_radius": criticality["blast_radius"],
            "analysis": ai_analysis
        }

    def _get_resource_type(self, resource_id):

        query = """
        MATCH (n {id:$id})
        RETURN labels(n)[0] AS type
        LIMIT 1
        """

        result = self.neo4j.query(
            query,
            id=resource_id
        )

        if result and len(result) > 0:
            return result[0]["type"]

        return "Unknown"
