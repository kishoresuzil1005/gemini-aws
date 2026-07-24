# knowledge/providers/aws/connectors/base_schema_connector.py
"""Base class for all AWS schema connectors.

Each connector follows a lifecycle:
    initialize -> health_check -> fetch -> validate -> version -> snapshot -> export -> shutdown

The base class provides common utilities such as logging, retry logic, and timeout handling.
"""

import abc
import logging
import time
from typing import Any, Callable, Optional

from .connector_config import ConnectorConfig
from .connector_exceptions import ConnectorError

logger = logging.getLogger(__name__)


class BaseSchemaConnector(abc.ABC):
    """Abstract base class for AWS schema connectors.

    Sub‑classes must implement the abstract methods to perform each lifecycle step.
    """

    def __init__(self, config: Optional[ConnectorConfig] = None):
        self.config = config or ConnectorConfig()
        self._initialized = False
        self._shutdown = False
        logger.debug("%s instantiated with config=%s", self.__class__.__name__, self.config)

    # ---------------------------------------------------------------------
    # Lifecycle hooks – subclasses must implement the core behaviour.
    # ---------------------------------------------------------------------
    @abc.abstractmethod
    def initialize(self) -> None:
        """Prepare any resources required for the connector (e.g., session, HTTP client)."""
        pass

    @abc.abstractmethod
    def health_check(self) -> bool:
        """Return ``True`` if the external source is reachable and healthy."""
        pass

    @abc.abstractmethod
    def fetch(self) -> bytes:
        """Download the raw schema payload and return it as ``bytes``.

        Implementations should respect ``self.config.timeout`` and use the shared
        ``_retry`` helper for transient failures.
        """
        pass

    @abc.abstractmethod
    def validate(self, raw_data: bytes) -> Any:
        """Validate the raw payload against the JSON schema for the source.

        Returns the parsed representation (usually a ``dict``) ready for version
        extraction and snapshot creation.
        """
        pass

    @abc.abstractmethod
    def version(self, parsed_data: Any) -> str:
        """Extract the source version string from the parsed payload.

        The returned version is used for snapshot metadata.
        """
        pass

    @abc.abstractmethod
    def snapshot(self, parsed_data: Any, version: str) -> str:
        """Persist an immutable snapshot of the raw data.

        Returns the absolute path to the snapshot directory that contains the
        ``specification.json`` and accompanying metadata files.
        """
        pass

    @abc.abstractmethod
    def export(self, snapshot_path: str) -> None:
        """Make the snapshot available to downstream components.

        In this milestone the export step simply records the location in a
        manifest – no further transformation is performed.
        """
        pass

    @abc.abstractmethod
    def shutdown(self) -> None:
        """Clean up any resources allocated during ``initialize``.
        """
        pass

    # ---------------------------------------------------------------------
    # Helper utilities shared by all connectors.
    # ---------------------------------------------------------------------
    def _retry(self, func: Callable[[], Any], *args, **kwargs) -> Any:
        """Execute *func* with retry logic based on the connector configuration.

        The retry policy respects ``self.config.retry_attempts`` and
        ``self.config.retry_backoff`` (seconds).  Exponential back‑off with jitter
        is applied between attempts.
        """
        attempts = self.config.retry_attempts
        backoff = self.config.retry_backoff
        for attempt in range(1, attempts + 1):
            try:
                logger.debug(
                    "%s attempt %d/%d", func.__name__, attempt, attempts
                )
                return func(*args, **kwargs)
            except Exception as exc:
                if attempt == attempts:
                    logger.error(
                        "%s failed after %d attempts: %s", func.__name__, attempts, exc
                    )
                    raise ConnectorError(str(exc)) from exc
                sleep_time = backoff * (2 ** (attempt - 1))
                logger.warning(
                    "%s failed (attempt %d). Retrying in %.1f seconds: %s",
                    func.__name__,
                    attempt,
                    sleep_time,
                    exc,
                )
                time.sleep(sleep_time)

    def run(self) -> str:
        """Convenient entry point that runs the full lifecycle.

        Returns the path to the created snapshot directory.
        """
        if self._shutdown:
            raise ConnectorError("Connector has already been shut down")
        self.initialize()
        if not self.health_check():
            raise ConnectorError("Health check failed")
        raw = self._retry(self.fetch)
        parsed = self.validate(raw)
        ver = self.version(parsed)
        snap_path = self.snapshot(parsed, ver)
        self.export(snap_path)
        self.shutdown()
        self._shutdown = True
        return snap_path
