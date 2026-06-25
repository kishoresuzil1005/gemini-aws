import time

from app.database import (
    SessionLocal,
    ResourceDB,
    MetricDB
)

from app.providers.aws.cloudwatch import (
    CloudWatchMetrics
)


class MetricCollector:

    @staticmethod
    def collect():

        db = SessionLocal()

        try:

            resources = (
                db.query(ResourceDB)
                .filter(
                    ResourceDB.resource_type
                    == "EC2"
                )
                .all()
            )

            for resource in resources:

                cpu = (
                    CloudWatchMetrics
                    .get_ec2_cpu(
                        resource.cloud_account_id or 1,
                        resource.resource_id
                    )
                )

                metric = MetricDB(

                    resource_id=
                    resource.resource_id,

                    name=
                    "CPUUtilization",

                    value=
                    cpu,

                    timestamp=
                    int(
                        time.time()
                        * 1000
                    )
                )

                db.add(metric)

            db.commit()

        finally:

            db.close()
