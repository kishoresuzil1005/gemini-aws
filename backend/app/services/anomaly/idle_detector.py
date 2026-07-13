from app.models import MetricDB


class IdleResourceDetector:

    CPU_THRESHOLD = 5

    @staticmethod
    def detect(db):

        results = []

        metrics = (
            db.query(MetricDB)
            .filter(
                MetricDB.name == "CPUUtilization"
            )
            .all()
        )

        for metric in metrics:

            if metric.value < 5:

                results.append({

                    "resource_id":
                    metric.resource_id,

                    "issue":
                    "Idle Resource",

                    "recommendation":
                    "Review and stop instance"
                })

        return result