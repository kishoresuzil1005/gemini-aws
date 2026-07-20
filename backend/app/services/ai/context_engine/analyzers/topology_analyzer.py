"""TopologyAnalyzer – Analyses raw graph topology (node counts, edge density, connected components).

Status: ``stub``

Replace the body of :meth:`analyze` with real logic in a future phase.
"""

from typing import Any, Dict

from .base_analyzer import BaseAnalyzer
from ..models import AIContext


class TopologyAnalyzer(BaseAnalyzer):
    """Analyses raw graph topology (node counts, edge density, connected components)."""

    name = "topology"

    def analyze(self, context: AIContext) -> Dict[str, Any]:
        """Perform topology analysis.

        TODO: Implement in a future phase.
        """
        return {
            "status": "not_implemented",
            "analyzer": self.name,
            "findings": [],
            "summary": {},
        }
