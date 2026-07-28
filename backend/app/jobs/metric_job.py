from app.core.logging import get_logger
logger = get_logger(__name__)
from app.services.metrics.collector import (
    MetricCollector
)


def run_metric_job():

    logger.debug(
        "[JOB] Collecting metrics..."
    )

    MetricCollector.collect()

    logger.debug(
        "[JOB] Metrics collected."
    )
