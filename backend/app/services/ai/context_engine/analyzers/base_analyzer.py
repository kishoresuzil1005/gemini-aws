"""Base class for all AI Context Engine analyzers."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..models import AIContext


class BaseAnalyzer(ABC):
    """Every analyzer must inherit from this class.

    Analyzers receive an assembled :class:`~models.AIContext` and produce
    a structured result dict.  They must never modify the context.

    Design rules
    ------------
    * Analyzers are stateless.
    * Analyzers operate only on data already in :class:`~models.AIContext`.
    * Analyzers never call providers or external APIs directly.
    * Analysis results are separate from provider data – do not overwrite
      any provider section.
    """

    name: str = "base"

    @abstractmethod
    def analyze(self, context: AIContext) -> Dict[str, Any]:
        """Perform analysis and return a structured result dict."""
        ...
