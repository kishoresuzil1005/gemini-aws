# knowledge/catalog/catalog_loader.py
"""Handles persistence and serialization of the catalog."""

import json
import logging
from typing import List

from .catalog_models import CanonicalResource

logger = logging.getLogger(__name__)

class CatalogLoader:
    """Manages writing and reading the catalog to/from persistent storage."""

    def save(self, filepath: str, resources: List[CanonicalResource]) -> None:
        """Serializes the canonical resources to a JSON line format or flat JSON."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                # Simplified list dump; in prod this would stream JSONL
                data = [r.dict() for r in resources]
                json.dump(data, f, indent=2)
            logger.info(f"Catalog saved to {filepath}")
        except Exception as exc:
            logger.error(f"Failed to save catalog: {exc}")

    def load(self, filepath: str) -> List[CanonicalResource]:
        """Deserializes canonical resources from storage."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [CanonicalResource(**item) for item in data]
        except Exception as exc:
            logger.error(f"Failed to load catalog: {exc}")
            return []
