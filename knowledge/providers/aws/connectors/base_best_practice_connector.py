# knowledge/providers/aws/connectors/base_best_practice_connector.py
"""Base class for AWS security‑related best‑practice knowledge connectors.

Extends :class:`BaseSchemaConnector` with additional lifecycle steps for discovering
document identifiers and fetching their metadata.
"""

import abc
import json
import logging
from typing import Any, List

from .base_schema_connector import BaseSchemaConnector
from .connector_config import ConnectorConfig
from .connector_exceptions import ConnectorError, InitializationError, DiscoveryError

logger = logging.getLogger(__name__)


class BaseBestPracticeConnector(BaseSchemaConnector, abc.ABC):
    """Abstract base for security best‑practice connectors.

    Sub‑classes must implement :meth:`discover_documents` and
    :meth:`fetch_metadata` to retrieve structured security knowledge.
    """

    def __init__(self, config: ConnectorConfig | None = None):
        super().__init__(config)
        self._documents: List[Any] = []

    @abc.abstractmethod
    def discover_documents(self) -> List[Any]:
        """Return a list of identifiers (IDs, ARNs, URLs, etc.) for the source
        documents that will be processed.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_metadata(self, document: Any) -> dict:
        """Given a document identifier, return a JSON‑serialisable dictionary
        containing the security metadata.
        """
        raise NotImplementedError

    def initialize(self) -> None:
        """Run base initialisation then discover documents.
        """
        try:
            super().initialize()
        except Exception as exc:
            raise InitializationError(str(exc)) from exc
        try:
            self._documents = self.discover_documents()
            logger.debug("%s discovered %d documents", self.__class__.__name__, len(self._documents))
        except Exception as exc:
            raise DiscoveryError(str(exc)) from exc

    def _collect_all_metadata(self) -> List[dict]:
        metadata: List[dict] = []
        for doc in self._documents:
            try:
                meta = self.fetch_metadata(doc)
                metadata.append(meta)
            except Exception as exc:
                logger.error("Failed to fetch metadata for %s: %s", doc, exc)
        return metadata

    def fetch(self) -> bytes:
        """Fetch all metadata and serialise to JSON ``bytes``.
        """
        all_meta = self._collect_all_metadata()
        return json.dumps(all_meta, separators=(",", ":")).encode("utf-8")
