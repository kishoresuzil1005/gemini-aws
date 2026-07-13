from sqlalchemy import text

from app.database import SessionLocal
from app.database_neo4j import driver

from app.services.ai.rag_service import RAGService


class ArchitectureReviewService:

    def __init__(self):
        self.rag = RAGService()

    def review(self):

        db = SessionLocal()

        try:

            #
            # PostgreSQL Summary
            #

            total_resources = db.execute(
                text("SELECT COUNT(*) FROM resource_nodes")
            ).scalar()

            resource_types = db.execute(
                text("""
                SELECT resource_type,
                       COUNT(*) AS total
                FROM resource_nodes
                GROUP BY resource_type
                ORDER BY total DESC
                """)
            ).fetchall()

            #
            # Neo4j Summary
            #

            total_nodes = 0
            total_relationships = 0
            critical_assets = []

            if driver:
                with driver.session() as session:

                    total_nodes = session.run(
                        """
                        MATCH (n)
                        RETURN count(n) AS total
                        """
                    ).single()["total"]

                    total_relationships = session.run(
                        """
                        MATCH ()-[r]->()
                        RETURN count(r) AS total
                        """
                    ).single()["total"]

                #
                # Critical Assets
                #

                with driver.session() as session:

                    result = session.run("""
                    MATCH (n)

                    OPTIONAL MATCH (a)-[]->(n)
                    WITH n,count(a) AS upstream

                    OPTIONAL MATCH (n)-[]->(b)
                    WITH n,upstream,count(b) AS downstream

                    RETURN
                        n.id AS id,
                        labels(n)[0] AS type,
                        upstream,
                        downstream,
                        upstream+downstream AS score

                    ORDER BY score DESC

                    LIMIT 10
                    """)

                    for row in result:

                        critical_assets.append({

                            "resource": row["id"],

                            "type": row["type"],

                            "score": row["score"]

                        })

            #
            # AWS Best Practices
            #

            rag = self.rag.query_rag(
                "AWS architecture review best practices",
                limit=5
            )

            #
            # Findings
            #

            findings = []

            if total_resources == 0:
                findings.append(
                    "No cloud resources discovered."
                )

            if total_relationships == 0:
                findings.append(
                    "No resource relationships found."
                )

            if total_resources > 0:
                findings.append(
                    f"{total_resources} cloud resources discovered."
                )

            #
            # Recommendations
            #

            recommendations = [

                "Enable CloudTrail auditing.",

                "Enable CloudWatch monitoring.",

                "Review Security Groups.",

                "Review IAM permissions.",

                "Enable Multi-AZ for production databases."

            ]

            return {

                "summary": {

                    "resources": total_resources,

                    "relationships": total_relationships,

                    "critical_assets": len(critical_assets)

                },

                "resource_types": [

                    {

                        "type": row.resource_type,

                        "count": row.total

                    }

                    for row in resource_types

                ],

                "critical_assets": critical_assets,

                "findings": findings,

                "recommendations": recommendations,

                "best_practices": rag["answer"]

            }

        finally:

            db.close()


# Backward-compatible alias for architecture_service.py
ArchitectureReview = ArchitectureReviewServic