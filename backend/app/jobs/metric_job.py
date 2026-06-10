from app.services.metrics.collector import (
    MetricCollector
)


def run_metric_job():

    print(
        "[JOB] Collecting metrics..."
    )

    MetricCollector.collect()

    print(
        "[JOB] Metrics collected."
    )
