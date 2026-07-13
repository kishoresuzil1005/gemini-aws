from app.services.graph.graph_analysis_service import GraphAnalysisService
from app.services.ai.rag_service import RAGService


class FailureAnalysisService:

    def __init__(self):
        self.rag = RAGService()

    def analyze(self, resource_id: str):

        graph_service = GraphAnalysisService()

        try:

            #
            # Downstream
            #

            downstream = graph_service.downstream_dependencies(resource_id)

            downstream_resources = [

                {

                    "id": r["id"],

                    "type": r.get("labels", ["Resource"])[0] if r.get("labels") else "Resource"

                }

                for r in downstream

            ]

            #
            # Upstream
            #

            upstream = graph_service.upstream_dependencies(resource_id)

            upstream_resources = [

                {

                    "id": r["id"],

                    "type": r.get("labels", ["Resource"])[0] if r.get("labels") else "Resource"

                }

                for r in upstream

            ]

            #
            # Blast Radius
            #

            blast_data = graph_service.blast_radius(resource_id)
            blast_radius = blast_data.get("impacted", 0)

        finally:

            graph_service.close()

        #
        # Risk
        #

        if blast_radius >= 10:

            risk = "CRITICAL"

        elif blast_radius >= 5:

            risk = "HIGH"

        elif blast_radius >= 2:

            risk = "MEDIUM"

        else:

            risk = "LOW"

        #
        # AWS Best Practices
        #

        rag = self.rag.query_rag(

            f"What are AWS best practices if {resource_id} fails?",

            limit=5

        )

        #
        # Recommendations
        #

        recommendations = [

            "Enable Multi-AZ.",

            "Enable Automated Backups.",

            "Review Disaster Recovery.",

            "Enable CloudWatch Alarms.",

            "Document Recovery Runbook."

        ]

        return {

            "resource": resource_id,

            "risk": risk,

            "blast_radius": blast_radius,

            "upstream": upstream_resources,

            "downstream": downstream_resources,

            "recommendations": recommendations,

            "best_practices": rag["answer"]

        }