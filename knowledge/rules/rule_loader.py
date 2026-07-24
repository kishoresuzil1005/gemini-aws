# knowledge/rules/rule_loader.py
"""Handles persistence and serialization of the Rule Catalog."""

import json
import logging
from typing import List

from .rule_models import CanonicalRule

logger = logging.getLogger(__name__)

class RuleLoader:
    """Manages writing and reading the Rule Catalog to/from disk."""

    def save(self, filepath: str, rules: List[CanonicalRule]) -> None:
        """Serializes the canonical rules to JSON."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                data = [r.dict() for r in rules]
                json.dump(data, f, indent=2)
            logger.info(f"Rule Catalog saved to {filepath}")
        except Exception as exc:
            logger.error(f"Failed to save rule catalog: {exc}")

    def load(self, filepath: str) -> List[CanonicalRule]:
        """Deserializes canonical rules from storage."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CanonicalRule(**item) for item in data]
        except Exception as exc:
            logger.error(f"Failed to load rule catalog: {exc}")
            return []
