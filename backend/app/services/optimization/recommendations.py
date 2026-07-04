from app.models import ResourceDB
from app.services.cost.pricing_service import PricingService

from app.services.optimization.ec2_optimizer import EC2Optimizer
from app.services.optimization.rds_optimizer import RDSOptimizer
from app.services.optimization.ebs_optimizer import EBSOptimizer


class RecommendationEngine:

    @staticmethod
    def generate(db):

        resources = (
            db.query(ResourceDB)
            .all()
        )

        pricing_service = (
            PricingService(db)
        )

        recommendations = []

        recommendations.extend(
            EC2Optimizer.analyze(
                db,
                resources,
                pricing_service
            )
        )

        recommendations.extend(
            RDSOptimizer.analyze(
                db,
                resources,
                pricing_service
            )
        )

        recommendations.extend(
            EBSOptimizer.analyze(
                resources
            )
        )

        return recommendations

    @staticmethod
    def get_recommendations(db, cloud_account_id=1):
        """
        Backward compatible bridge method mapping to generate(db)
        """
        return RecommendationEngine.generate(db)


# Alias for backward compatibility mapping
RecommendationsEngine = RecommendationEngine
