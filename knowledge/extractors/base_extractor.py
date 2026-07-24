# knowledge/extractors/base_extractor.py
"""Abstract base class for all extractors in the M6 engine."""

import abc
import logging
from typing import Any, List

from .extractor_context import ExtractorContext
from .knowledge_candidate import KnowledgeCandidate

logger = logging.getLogger(__name__)


class BaseExtractor(abc.ABC):
    """Base class for isolating specific Knowledge Candidates from parsed structures."""

    def __init__(self):
        self.name = self.__class__.__name__

    @abc.abstractmethod
    def extract(self, parsed_data: Any, context: ExtractorContext) -> List[KnowledgeCandidate]:
        """Extract structured candidates from parsed data.
        
        Args:
            parsed_data: The intermediate representation (e.g., dictionary) from the Parser.
            context: Contextual metadata (provider, source format, etc.).
            
        Returns:
            A list of instantiated KnowledgeCandidates.
        """
        raise NotImplementedError
