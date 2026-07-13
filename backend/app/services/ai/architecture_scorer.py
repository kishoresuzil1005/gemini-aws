from app.services.ai.architecture_review import ArchitectureReviewService


class ArchitectureScorer:

    def __init__(self):
        self.review_service = ArchitectureReviewService()

    def score(self):

        review = self.review_service.review()

        resources = review["summary"]["resources"]
        relationships = review["summary"]["relationships"]
        critical_assets = review["summary"]["critical_assets"]

        #
        # Pillar Scores
        #

        availability = min(10, max(1, relationships // 5))

        security = 8

        reliability = min(10, max(1, critical_assets + 2))

        performance = 8

        cost = 7

        operational = 8

        sustainability = 8

        overall = round(

            (

                availability +

                security +

                reliability +

                performance +

                cost +

                operational +

                sustainability

            ) / 7 * 10

        )

        #
        # Grade
        #

        if overall >= 90:
            grade = "A+"

        elif overall >= 80:
            grade = "A"

        elif overall >= 70:
            grade = "B"

        elif overall >= 60:
            grade = "C"

        else:
            grade = "D"

        return {

            "overall_score": overall,

            "grade": grade,

            "pillar_scores": {

                "availability": availability,

                "security": security,

                "reliability": reliability,

                "performance_efficiency": performance,

                "cost_optimization": cost,

                "operational_excellence": operational,

                "sustainability": sustainability

            }

        