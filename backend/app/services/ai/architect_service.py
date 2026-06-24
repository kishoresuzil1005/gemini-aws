from app.services.graph.criticality_service import CriticalityService
from app.services.graph.graph_analysis_service import GraphAnalysisService
from app.services.graph.neo4j_service import Neo4jService


class ArchitectService:

    def __init__(self):
        self.criticality = CriticalityService()
        self.analysis = GraphAnalysisService()
        self.neo4j = Neo4jService()

    def analyze(self, resource_id: str):

        criticality = self.criticality.calculate(resource_id)

        resource_type = self._get_resource_type(resource_id)

        findings = self._generate_findings(
            resource_type,
            criticality
        )

        recommendations = self._generate_recommendations(
            resource_type,
            criticality
        )

        return {
            "resource": resource_id,
            "resource_type": resource_type,
            "risk": criticality["criticality"],
            "criticality_score": criticality["score"],
            "blast_radius": criticality["blast_radius"],
            "upstream": criticality["upstream"],
            "downstream": criticality["downstream"],
            "findings": findings,
            "recommendations": recommendations
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

    def _generate_findings(
        self,
        resource_type,
        criticality
    ):

        findings = []

        if criticality["score"] >= 15:
            findings.append(
                "Critical infrastructure component."
            )

        if criticality["blast_radius"] >= 5:
            findings.append(
                f"Failure may impact {criticality['blast_radius']} resources."
            )

        if resource_type == "RDS":
            findings.append(
                "Database service detected."
            )

        if resource_type == "EC2":
            findings.append(
                "Compute workload detected."
            )

        if resource_type == "Lambda":
            findings.append(
                "Serverless workload detected."
            )

        return findings

    def _generate_recommendations(
        self,
        resource_type,
        criticality
    ):

        if resource_type == "RDS":
            return [
                "Enable Multi-AZ",
                "Enable Automated Backups",
                "Enable Enhanced Monitoring"
            ]

        if resource_type == "EC2":
            return [
                "Enable CloudWatch Agent",
                "Review Security Groups",
                "Enable Auto Scaling"
            ]

        if resource_type == "Lambda":
            return [
                "Review IAM permissions",
                "Enable X-Ray tracing",
                "Configure Dead Letter Queue"
            ]

        if resource_type == "VPC":
            return [
                "Review route tables",
                "Audit Internet exposure",
                "Verify NACL rules"
            ]

        return [
            "Review architecture",
            "Monitor resource utilization"
        ]
