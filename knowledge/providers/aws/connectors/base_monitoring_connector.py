# knowledge/providers/aws/connectors/base_monitoring_connector.py
"""Base class for AWS monitoring and operational knowledge connectors.

Extends :class:`BaseSchemaConnector` with additional lifecycle steps for
discovering monitoring definitions (namespaces, alarms, events) and fetching
their metadata.
"""

import abc
import json
import logging
from typing import Any, List

from .base_schema_connector import BaseSchemaConnector
from .connector_config import ConnectorConfig
from .connector_exceptions import ConnectorError, InitializationError, DiscoveryError

logger = logging.getLogger(__name__)


class BaseMonitoringConnector(BaseSchemaConnector, abc.ABC):
    """Abstract base for monitoring and operational knowledge connectors.

    Sub‑classes must implement :meth:`discover_definitions` and
    :meth:`fetch_metadata` to retrieve structured operational knowledge.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self._definitions: List[Any] = []

    @abc.abstractmethod
    def discover_definitions(self) -> List[Any]:
        """Return a list of identifiers (namespaces, ARNs, URLs, etc.) for the
        definitions that will be processed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_metadata(self, definition: Any) -> dict:
        """Given a definition identifier, return a JSON‑serialisable dictionary
        containing the operational metadata.
        """
        raise NotImplementedError

    def initialize(self) -> None:
        """Run base initialisation then discover definitions.
        """
        try:
            super().initialize()
        except Exception as exc:
            raise InitializationError(str(exc)) from exc
        try:
            self._definitions = self.discover_definitions()
            logger.debug("%s discovered %d definitions", self.__class__.__name__, len(self._definitions))
        except Exception as exc:
            raise DiscoveryError(str(exc)) from exc

    def _collect_all_metadata(self) -> List[dict]:
        metadata: List[dict] = []
        for d in self._definitions:
            try:
                meta = self.fetch_metadata(d)
                metadata.append(meta)
            except Exception as exc:
                logger.error("Failed to fetch metadata for %s: %s", d, exc)
        return metadata

    def fetch(self) -> bytes:
        """Fetch all metadata and serialise to JSON ``bytes``.
        """
        all_meta = self._collect_all_metadata()
        return json.dumps(all_meta, separators=(",", ":")).encode("utf-8")
