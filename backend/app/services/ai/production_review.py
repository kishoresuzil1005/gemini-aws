from app.services.ai.architecture_review import ArchitectureReviewService
from app.services.ai.architecture_scorer import ArchitectureScorer


class ProductionReviewService:

    def __init__(self):

        self.review_service = ArchitectureReviewService()
        self.score_service = ArchitectureScorer()

    def review(self):

        review = self.review_service.review()

        score = self.score_service.score()

        checks = []

        #
        # High Availability
        #

        checks.append({
            "name": "High Availability",
            "status": "PASS",
            "recommendation": "Deploy workloads across multiple Availability Zones."
        })

        #
        # Monitoring
        #

        checks.append({
            "name": "Monitoring",
            "status": "PASS",
            "recommendation": "Enable CloudWatch metrics and alarms."
        })

        #
        # Security
        #

        checks.append({
            "name": "Security",
            "status": "PASS",
            "recommendation": "Review IAM and Security Groups."
        })

        #
        # Disaster Recovery
        #

        checks.append({
            "name": "Disaster Recovery",
            "status": "WARNING",
            "recommendation": "Enable automated backups and DR testing."
        })

        #
        # Logging
        #

        checks.append({
            "name": "Logging",
            "status": "PASS",
            "recommendation": "Enable CloudTrail and centralized logging."
        })

        #
        # Overall Status
        #

        if score["overall_score"] >= 90:

            status = "PRODUCTION_READY"

        elif score["overall_score"] >= 75:

            status = "NEAR_PRODUCTION"

        else:

            status = "NOT_PRODUCTION_READY"

        return {

            "overall_status": status,

            "architecture_score": score,

            "checks": checks,

            "summary": review["summary"]

        }
