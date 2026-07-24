# knowledge/normalization/base_normalizer.py
"""Abstract base class for all normalizers."""

import abc
import logging
from typing import List

from .normalization_context import NormalizationContext
from .normalization_models import CanonicalModel
from ..extractors.knowledge_candidate import KnowledgeCandidate

logger = logging.getLogger(__name__)

class BaseNormalizer(abc.ABC):
    """Base class for transforming Candidates into Canonical Knowledge Models."""

    def __init__(self):
        self.name = self.__class__.__name__

    @abc.abstractmethod
    def normalize(self, candidates: List[KnowledgeCandidate], context: NormalizationContext) -> List[CanonicalModel]:
        """Convert a list of provider-specific candidates into canonical models."""
        raise NotImplementedError
