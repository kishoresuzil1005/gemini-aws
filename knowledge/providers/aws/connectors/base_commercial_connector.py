# knowledge/providers/aws/connectors/base_commercial_connector.py
"""Base class for commercial AWS schema connectors.

Extends :class:`BaseSchemaConnector` with authentication and discovery steps.
"""

import abc
import logging
from typing import Any, Optional

from .base_schema_connector import BaseSchemaConnector
from .connector_config import ConnectorConfig
from .connector_exceptions import ConnectorError, InitializationError, AuthenticationError, DiscoveryError

logger = logging.getLogger(__name__)


class BaseCommercialConnector(BaseSchemaConnector, abc.ABC):
    """Abstract base for commercial connectors (Pricing, Quotas, Region, Currency).

    Adds ``authenticate`` and ``discover`` abstract methods to the generic
    lifecycle defined in :class:`BaseSchemaConnector`.
    """

    def __init__(self, config: Optional[ConnectorConfig] = None):
        super().__init__(config)
        self._authenticated = False
        self._discovered = False

    @abc.abstractmethod
    def authenticate(self) -> None:
        """Perform any required authentication (e.g., AWS SDK credential chain).
        May be a no‑op for publicly accessible endpoints.
        """
        pass

    @abc.abstractmethod
    def discover(self) -> None:
        """Discover API version or available endpoints before fetching data.
        Should set internal attributes needed for ``fetch``.
        """
        pass

    def initialize(self) -> None:
        """Default implementation calls ``authenticate`` and ``discover``.
        Sub‑classes can extend but must call ``super().initialize()``.
        """
        try:
            self.authenticate()
            self._authenticated = True
            self.discover()
            self._discovered = True
            logger.debug("%s initialized (auth=%s, discovered=%s)", self.__class__.__name__, self._authenticated, self._discovered)
        except Exception as exc:
            raise InitializationError(str(exc)) from exc
