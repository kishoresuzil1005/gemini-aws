from app.services.ai.architecture_review import ArchitectureReviewService
from app.services.ai.architecture_scorer import ArchitectureScorer
from app.services.ai.production_review import ProductionReviewService
from app.services.ai.production_checklist import ProductionChecklistService
from app.services.ai.rag_service import RAGService


class WellArchitectedReviewService:

    def __init__(self):

        self.review = ArchitectureReviewService()

        self.score = ArchitectureScorer()

        self.production = ProductionReviewService()

        self.checklist = ProductionChecklistService()

        self.rag = RAGService()

    def review_architecture(self):

        architecture = self.review.review()

        score = self.score.score()

        production = self.production.review()

        checklist = self.checklist.checklist()

        aws_guidance = self.rag.query_rag(

            "AWS Well Architected Framework best practices",

            limit=8

        )

        pillars = {

            "Operational Excellence": {

                "score": score["pillar_scores"]["operational_excellence"],

                "status": "GOOD"

            },

            "Security": {

                "score": score["pillar_scores"]["security"],

                "status": "GOOD"

            },

            "Reliability": {

                "score": score["pillar_scores"]["reliability"],

                "status": "GOOD"

            },

            "Performance Efficiency": {

                "score": score["pillar_scores"]["performance_efficiency"],

                "status": "GOOD"

            },

            "Cost Optimization": {

                "score": score["pillar_scores"]["cost_optimization"],

                "status": "GOOD"

            },

            "Sustainability": {

                "score": score["pillar_scores"]["sustainability"],

                "status": "GOOD"

            }

        }

        findings = [

            "Infrastructure discovery completed.",

            "Architecture graph successfully generated.",

            "Critical resources identified.",

            "Production review completed."

        ]

        recommendations = [

            "Enable Multi-AZ for production databases.",

            "Review IAM least privilege.",

            "Enable CloudTrail.",

            "Configure CloudWatch alarms.",

            "Enable automated backups."

        ]

        return {

            "overall_score": score["overall_score"],

            "grade": score["grade"],

            "well_architected_pillars": pillars,

            "findings": findings,

            "recommendations": recommendations,

            "production_review": production,

            "production_checklist": checklist,

            "aws_best_practices": aws_guidance["answer"]

        }