import logging
from sqlalchemy.orm import Session

from app.database import ResourceDB
from app.services.cost.pricing_service import PricingService
from app.services.cost.ec2_cost import EC2CostCalculator
from app.services.cost.rds_cost import RDSCostCalculator
from app.services.cost.s3_cost import S3CostCalculator
from app.services.cost.lambda_cost import LambdaCostCalculator

logger = logging.getLogger("CostAggregator")


class CostAggregator:

    @staticmethod
    def calculate_account_monthly(
        db: Session,
        cloud_account_id: int
    ) -> dict:

        pricing_service = PricingService(db)

        resources = (
            db.query(ResourceDB)
            .filter(
                ResourceDB.cloud_account_id == cloud_account_id
            )
            .all()
        )

        if not resources:
            resources = db.query(ResourceDB).all()

        summary = {
            "ec2": 0.0,
            "rds": 0.0,
            "s3": 0.0,
            "lambda": 0.0,
            "ebs": 0.0,
            "alb": 0.0,
            "sqs": 0.0,
            "sns": 0.0,
            "total": 0.0
        }

        for r in resources:

            r_type = (
                r.resource_type.upper()
                if r.resource_type
                else ""
            )

            region = (
                r.region
                if getattr(r, "region", None)
                else "us-east-1"
            )

            metadata = {}

            if hasattr(r, "metadata") and r.metadata:
                metadata = r.metadata

            try:

                # -------------------------
                # EC2
                # -------------------------
                if r_type == "EC2":

                    inst_type = (
                        getattr(r, "instance_type", None)
                        or metadata.get("instance_type")
                    )

                    if inst_type:

                        cost = (
                            EC2CostCalculator
                            .calculate_instance_monthly(
                                pricing_service,
                                inst_type,
                                region
                            )
                        )

                        summary["ec2"] += cost

                # -------------------------
                # RDS
                # -------------------------
                elif r_type == "RDS":

                    db_class = (
                        getattr(r, "instance_class", None)
                        or metadata.get("instance_class")
                    )

                    if db_class:

                        cost = (
                            RDSCostCalculator
                            .calculate_rds_monthly(
                                pricing_service,
                                db_class,
                                region
                            )
                        )

                        summary["rds"] += cost

                # -------------------------
                # S3
                # -------------------------
                elif r_type == "S3":

                    size_gb = (
                        getattr(r, "size_gb", None)
                        or metadata.get("size_gb", 0)
                    )

                    cost = (
                        S3CostCalculator
                        .calculate_s3_monthly(
                            pricing_service,
                            size_gb=size_gb,
                            storage_class="Standard"
                        )
                    )

                    summary["s3"] += cost

                # -------------------------
                # Lambda
                # -------------------------
                elif r_type in ["LAMBDA", "FUNCTION"]:

                    monthly_requests = (
                        getattr(r, "monthly_requests", None)
                        or metadata.get(
                            "monthly_requests",
                            0
                        )
                    )

                    memory_size_mb = (
                        getattr(r, "memory_size", None)
                        or metadata.get(
                            "memory_size",
                            128
                        )
                    )

                    avg_duration_ms = (
                        getattr(r, "avg_duration_ms", None)
                        or metadata.get(
                            "avg_duration_ms",
                            100
                        )
                    )

                    cost = (
                        LambdaCostCalculator
                        .calculate_lambda_monthly(
                            memory_size_mb=
                            memory_size_mb,

                            monthly_requests=
                            monthly_requests,

                            avg_duration_ms=
                            avg_duration_ms
                        )
                    )

                    summary["lambda"] += cost

                # -------------------------
                # EBS
                # -------------------------
                elif r_type == "EBS":

                    gb_size = (
                        getattr(r, "size_gb", None)
                        or metadata.get(
                            "size_gb",
                            0
                        )
                    )

                    summary["ebs"] += (
                        gb_size * 0.08
                    )

                # -------------------------
                # ALB
                # -------------------------
                elif r_type in [
                    "ALB",
                    "ELB",
                    "GATEWAY"
                ]:

                    summary["alb"] += 22.50

                # -------------------------
                # SQS
                # -------------------------
                elif r_type == "SQS":

                    summary["sqs"] += 18.20

                # -------------------------
                # SNS
                # -------------------------
                elif r_type == "SNS":

                    summary["sns"] += 8.50

            except Exception as ex:

                logger.error(
                    f"Cost calculation failed "
                    f"for {r_type}: {ex}"
                )

        total_sum = sum(
            value
            for key, value
            in summary.items()
            if key != "total"
        )

        summary["total"] = round(
            total_sum,
            2
        )

        for key in summary.keys():

            if key != "total":

                summary[key] = round(
                    summary[key],
                    2
                )

        return summary