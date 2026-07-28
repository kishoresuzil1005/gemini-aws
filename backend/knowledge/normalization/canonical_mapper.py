# knowledge/normalization/canonical_mapper.py
"""Handles mapping logic to instantiate strict Canonical Models."""

import logging
from typing import Dict, Any, Type, Optional

from .normalization_models import CanonicalModel

logger = logging.getLogger(__name__)

class CanonicalMapper:
    """Instantiates strict Pydantic canonical models from generic dictionaries."""

    def map_to_model(self, mapped_dict: Dict[str, Any], target_class: Type[CanonicalModel]) -> Optional[CanonicalModel]:
        """Attempt to instantiate the target Pydantic class."""
        try:
            return target_class(**mapped_dict)
        except Exception as exc:
            logger.warning("Failed to canonicalize to %s: %s", target_class.__name__, exc)
            return None
