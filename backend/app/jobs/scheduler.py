from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.jobs.metric_job import (
    run_metric_job
)

from app.jobs.cost_job import (
    run_cost_job
)

from app.jobs.optimization_job import (
    run_optimization_job
)

from app.jobs.anomaly_job import (
    run_anomaly_job
)

from app.jobs.ai_job import (
    run_ai_job
)

scheduler = (
    BackgroundScheduler()
)


def start_scheduler():

    scheduler.add_job(
        run_metric_job,
        "interval",
        minutes=5
    )

    scheduler.add_job(
        run_cost_job,
        "interval",
        hours=1
    )

    scheduler.add_job(
        run_optimization_job,
        "interval",
        minutes=15
    )

    scheduler.add_job(
        run_anomaly_job,
        "interval",
        minutes=15
    )

    scheduler.add_job(
        run_ai_job,
        "interval",
        hours=1
    )

    scheduler.start()

    print(
        "[SCHEDULER] Started"
    )

    # Pre-warm metric collection caches immediately on startup
    try:
        run_metric_job()
    except Exception as e:
        import logging
        logging.getLogger("Scheduler").warning(f"Initial background metrics harvest deferred: {e}")
