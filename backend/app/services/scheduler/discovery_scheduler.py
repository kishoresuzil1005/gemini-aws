"""
Discovery Scheduler — Production Implementation
Continuously runs provider discovery on a configurable cadence using APScheduler.
"""
import logging
import os
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DiscoveryScheduler:
    """
    Continuous discovery scheduler backed by APScheduler.
    Supports:
    - Periodic discovery (every N minutes)
    - One-time manual triggers
    - Mission-triggered discovery
    - Provider-specific schedules
    - Concurrent discovery with capped parallelism
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._scheduler = None
        self._jobs: Dict[str, Any] = {}
        self._discovery_fn: Optional[Callable] = None
        self._initialize_scheduler()

    def _initialize_scheduler(self):
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.executors.pool import ThreadPoolExecutor

            executors = {"default": ThreadPoolExecutor(self.max_workers)}
            job_defaults = {"coalesce": True, "max_instances": 1, "misfire_grace_time": 60}

            self._scheduler = BackgroundScheduler(
                executors=executors,
                job_defaults=job_defaults,
            )
            logger.info("DiscoveryScheduler initialized with APScheduler.")
        except ImportError:
            logger.warning("APScheduler not installed. Run: pip install apscheduler. Scheduler disabled.")
            self._scheduler = None

    def register_discovery_fn(self, fn: Callable):
        """Register the function to call for each scheduled discovery run."""
        self._discovery_fn = fn
        logger.info(f"Discovery function registered: {fn.__name__}")

    def add_provider_schedule(
        self,
        provider: str,
        interval_minutes: int = 5,
        region: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """
        Adds a recurring discovery job for a provider.

        Args:
            provider: Cloud provider name (aws, azure, gcp, kubernetes).
            interval_minutes: Run every N minutes.
            region: Specific region or None for all regions.
            job_id: Optional custom job ID.

        Returns:
            Job ID of the scheduled job.
        """
        if not self._scheduler:
            logger.warning("Scheduler not available. Cannot add job.")
            return ""

        effective_id = job_id or f"discover_{provider}_{region or 'all'}"

        if effective_id in self._jobs:
            self.remove_job(effective_id)

        def discovery_wrapper():
            logger.info(f"[Scheduler] Running discovery: provider={provider}, region={region}")
            if self._discovery_fn:
                try:
                    self._discovery_fn(provider=provider, region=region)
                except Exception as e:
                    logger.error(f"[Scheduler] Discovery failed for {provider}: {e}", exc_info=True)

        job = self._scheduler.add_job(
            discovery_wrapper,
            trigger="interval",
            minutes=interval_minutes,
            id=effective_id,
            replace_existing=True,
        )

        self._jobs[effective_id] = job
        logger.info(f"Scheduled {provider} discovery every {interval_minutes}m — job: {effective_id}")
        return effective_id

    def add_cron_schedule(
        self,
        provider: str,
        cron_expression: str,
        region: Optional[str] = None,
        job_id: Optional[str] = None,
    ) -> str:
        """
        Adds a cron-based discovery job.

        Args:
            cron_expression: Standard 5-field cron (minute hour day month day_of_week).
        """
        if not self._scheduler:
            return ""

        from apscheduler.triggers.cron import CronTrigger

        parts = cron_expression.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expression}")

        effective_id = job_id or f"cron_{provider}_{cron_expression.replace(' ', '_')}"

        def discovery_wrapper():
            logger.info(f"[CronScheduler] Running discovery: provider={provider}, region={region}")
            if self._discovery_fn:
                try:
                    self._discovery_fn(provider=provider, region=region)
                except Exception as e:
                    logger.error(f"[CronScheduler] Discovery failed: {e}", exc_info=True)

        trigger = CronTrigger(
            minute=parts[0], hour=parts[1], day=parts[2], month=parts[3], day_of_week=parts[4]
        )

        job = self._scheduler.add_job(
            discovery_wrapper, trigger=trigger, id=effective_id, replace_existing=True
        )
        self._jobs[effective_id] = job
        logger.info(f"Cron-scheduled {provider} discovery: {cron_expression} — job: {effective_id}")
        return effective_id

    def trigger_now(self, provider: str, region: Optional[str] = None) -> bool:
        """Manually triggers a one-shot discovery immediately."""
        if not self._discovery_fn:
            logger.warning("No discovery function registered.")
            return False

        import threading
        def run():
            try:
                self._discovery_fn(provider=provider, region=region)
            except Exception as e:
                logger.error(f"Manual discovery failed for {provider}: {e}")

        t = threading.Thread(target=run, daemon=True)
        t.start()
        logger.info(f"Manual discovery triggered for {provider}/{region or 'all'}")
        return True

    def remove_job(self, job_id: str) -> bool:
        if not self._scheduler:
            return False
        try:
            self._scheduler.remove_job(job_id)
            self._jobs.pop(job_id, None)
            logger.info(f"Removed scheduled job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}")
            return False

    def list_jobs(self) -> List[Dict[str, Any]]:
        if not self._scheduler:
            return []
        jobs = []
        for job in self._scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs

    def start(self):
        if self._scheduler and not self._scheduler.running:
            self._scheduler.start()
            logger.info("DiscoveryScheduler started.")

    def stop(self):
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("DiscoveryScheduler stopped.")

    @property
    def is_running(self) -> bool:
        return bool(self._scheduler and self._scheduler.running)


# Singleton instance
discovery_scheduler = DiscoveryScheduler()