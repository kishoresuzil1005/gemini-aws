from app.services.graph.criticality_service import CriticalityService
from app.services.graph.graph_analysis_service import GraphAnalysisService
from app.services.graph.neo4j_service import Neo4jService
from app.services.ai.ollama_service import OllamaService
from app.services.ai.graph_context import GraphContextBuilder
from app.services.ai.prompt_builder import PromptBuilder


class ArchitectService:

    def __init__(self):
        self.criticality = CriticalityService()
        self.analysis = GraphAnalysisService()
        self.neo4j = Neo4jService()
        self.ollama = OllamaService()
        self.graph_context = GraphContextBuilder()

    def analyze(self, resource_id: str):

        criticality = self.criticality.calculate(resource_id)
        resource_type = self._get_resource_type(resource_id)

        graph_context = self.graph_context.get_context(resource_id)

        #
        # Convert graph into readable text for the LLM
        #

        graph_summary = []

        graph_summary.append(f"Resource ID: {graph_context.get('resource')}")
        graph_summary.append(f"Resource Type: {graph_context.get('resource_type')}")
        graph_summary.append(f"Name: {graph_context.get('name')}")
        graph_summary.append(f"Provider: {graph_context.get('provider')}")
        graph_summary.append(f"Region: {graph_context.get('region')}")

        graph_summary.append("")
        graph_summary.append("Outgoing Relationships:")

        dependencies = graph_context.get("dependencies", [])

        if dependencies:
            for dep in dependencies:
                graph_summary.append(
                    f"- {dep['relationship']} -> "
                    f"{dep['type']} "
                    f"({dep['name']}) "
                    f"[{dep['id']}]"
                )
        else:
            graph_summary.append("- None")

        graph_summary.append("")
        graph_summary.append("Incoming Relationships:")

        incoming = graph_context.get("incoming_dependencies", [])

        if incoming:
            for dep in incoming:
                graph_summary.append(
                    f"- {dep['relationship']} <- "
                    f"{dep['type']} "
                    f"({dep['name']}) "
                    f"[{dep['id']}]"
                )
        else:
            graph_summary.append("- None")

        graph_summary.append("")
        graph_summary.append(f"Criticality Score: {criticality.get('criticality_score',0)}")
        graph_summary.append(
            f"Blast Radius: {criticality.get('details',{}).get('blast_radius',0)}"
        )

        graph_summary_text = "\n".join(graph_summary)

        prompt_builder = PromptBuilder()

        query = (
            f"Analyze the architecture, risk, and blast radius "
            f"for this {resource_type} resource ({resource_id}). "
            f"Use the cloud graph below as the primary source of truth."
        )

        architecture_context = {
            "failure_context": {
                "resource": resource_id,
                "criticality_score": criticality.get("criticality_score", 0),
                "blast_radius": criticality.get("details", {}).get("blast_radius", 0),
            }
        }

        prompt = prompt_builder.build(
            query=query,
            context=graph_summary_text,
            architecture_context=architecture_context
        )

        ai_response = self.ollama.generate(prompt)

        return {
            "resource": resource_id,
            "resource_type": resource_type,
            "risk": criticality.get("criticality_level", "Unknown"),
            "criticality_score": criticality.get("criticality_score", 0),
            "blast_radius": criticality.get("details", {}).get("blast_radius", 0),
            "graph_dependencies": graph_context,
            "ai_analysis": ai_response
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