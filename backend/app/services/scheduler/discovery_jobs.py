"""
Discovery Jobs — Production Implementation
Manages the queue and execution logic for per-provider discovery jobs.
"""
import logging
import time
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DiscoveryJobStatus:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class DiscoveryJob:
    """Represents a single discovery job for a provider+region."""

    def __init__(self, provider: str, region: Optional[str] = None):
        self.provider = provider
        self.region = region
        self.status = DiscoveryJobStatus.PENDING
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "region": self.region,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_seconds": round(self.completed_at - self.started_at, 3) if (self.started_at and self.completed_at) else None,
            "error": self.error,
        }


class DiscoveryJobs:
    """
    Queues and executes discovery jobs for all registered providers.
    Jobs can run sequentially or with limited parallelism.
    """

    def __init__(self):
        self._history: List[DiscoveryJob] = []

    def enqueue_job(
        self,
        provider: str,
        region: Optional[str] = None,
        discovery_fn: Optional[Callable] = None,
    ) -> DiscoveryJob:
        """
        Creates and immediately executes a discovery job.

        Args:
            provider: Cloud provider (aws, azure, gcp, kubernetes).
            region: Target region. None means all regions.
            discovery_fn: Callable that performs the discovery.

        Returns:
            Completed DiscoveryJob.
        """
        job = DiscoveryJob(provider=provider, region=region)
        job.status = DiscoveryJobStatus.RUNNING
        job.started_at = time.time()

        logger.info(f"Starting discovery job: {provider}/{region or 'all'}")

        try:
            if discovery_fn:
                result = discovery_fn(provider=provider, region=region)
                job.result = result
            job.status = DiscoveryJobStatus.SUCCESS
            logger.info(f"Discovery job completed: {provider}/{region or 'all'}")
        except Exception as e:
            job.status = DiscoveryJobStatus.FAILED
            job.error = str(e)
            logger.error(f"Discovery job failed: {provider}/{region or 'all'}: {e}", exc_info=True)
        finally:
            job.completed_at = time.time()
            self._history.append(job)

        return job

    def enqueue_all_providers(
        self,
        providers: List[str],
        discovery_fn: Optional[Callable] = None,
        regions: Optional[Dict[str, List[str]]] = None,
    ) -> List[DiscoveryJob]:
        """
        Runs discovery for all providers sequentially.

        Args:
            providers: List of provider names.
            discovery_fn: Callable(provider, region).
            regions: Map of provider -> [regions]. Uses default if not specified.
        """
        jobs = []
        for provider in providers:
            provider_regions = (regions or {}).get(provider, [None])
            for region in provider_regions:
                job = self.enqueue_job(provider=provider, region=region, discovery_fn=discovery_fn)
                jobs.append(job)
        return jobs

    def enqueue_all_providers_parallel(
        self,
        providers: List[str],
        discovery_fn: Optional[Callable] = None,
        regions: Optional[Dict[str, List[str]]] = None,
        max_workers: int = 4,
    ) -> List[DiscoveryJob]:
        """
        Runs discovery for all providers in parallel using ThreadPoolExecutor.
        """
        import concurrent.futures
        tasks = []
        for provider in providers:
            provider_regions = (regions or {}).get(provider, [None])
            for region in provider_regions:
                tasks.append((provider, region))

        jobs = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.enqueue_job, provider, region, discovery_fn): (provider, region)
                for provider, region in tasks
            }
            for future in concurrent.futures.as_completed(futures):
                try:
                    jobs.append(future.result())
                except Exception as e:
                    provider, region = futures[future]
                    logger.error(f"Parallel discovery failed for {provider}/{region}: {e}")

        return jobs

    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the most recent job history."""
        return [job.to_dict() for job in self._history[-limit:]]

    def get_summary(self) -> Dict[str, Any]:
        """Returns a summary of job outcomes."""
        total = len(self._history)
        succeeded = sum(1 for j in self._history if j.status == DiscoveryJobStatus.SUCCESS)
        failed = sum(1 for j in self._history if j.status == DiscoveryJobStatus.FAILED)
        return {
            "total_jobs": total,
            "succeeded": succeeded,
            "failed": failed,
            "success_rate": round(succeeded / total, 2) if total else 0,
        }