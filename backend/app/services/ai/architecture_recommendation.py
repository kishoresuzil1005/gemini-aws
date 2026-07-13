from app.services.ai.architecture_review import ArchitectureReviewService
from app.services.ai.architecture_scorer import ArchitectureScorer


class ArchitectureRecommendationService:

    def __init__(self):
        self.review_service = ArchitectureReviewService()
        self.score_service = ArchitectureScorer()

    def recommend(self):

        review = self.review_service.review()
        score = self.score_service.score()

        recommendations = []

        #
        # Database
        #

        resource_types = {
            item["type"]: item["count"]
            for item in review["resource_types"]
        }

        if resource_types.get("RDS", 0) > 0:
            recommendations.append({
                "priority": "HIGH",
                "category": "Database",
                "recommendation": "Enable Multi-AZ for all production RDS databases.",
                "benefit": "Improves availability and disaster recovery."
            })

        #
        # Security
        #

        recommendations.append({
            "priority": "HIGH",
            "category": "Security",
            "recommendation": "Review Security Group rules and enforce least privilege.",
            "benefit": "Reduces attack surface."
        })

        recommendations.append({
            "priority": "HIGH",
            "category": "Security",
            "recommendation": "Enable CloudTrail for auditing.",
            "benefit": "Provides complete audit history."
        })

        #
        # Monitoring
        #

        recommendations.append({
            "priority": "MEDIUM",
            "category": "Monitoring",
            "recommendation": "Enable CloudWatch metrics, alarms, and dashboards.",
            "benefit": "Improves operational visibility."
        })

        #
        # IAM
        #

        recommendations.append({
            "priority": "MEDIUM",
            "category": "IAM",
            "recommendation": "Review IAM roles and remove unused permissions.",
            "benefit": "Improves security posture."
        })

        #
        # Cost
        #

        recommendations.append({
            "priority": "LOW",
            "category": "Cost",
            "recommendation": "Review EC2 utilization using Compute Optimizer.",
            "benefit": "Potential monthly cost savings."
        })

        return {

            "overall_score": score["overall_score"],

            "grade": score["grade"],

            "recommendations": recommendations

        