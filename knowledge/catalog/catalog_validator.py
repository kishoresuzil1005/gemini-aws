# knowledge/catalog/catalog_validator.py
"""Enforces schema consistency and required properties for the Catalog."""

import logging
from typing import List

from .catalog_models import CanonicalResource
from .catalog_exceptions import CatalogValidationError

logger = logging.getLogger(__name__)

class CatalogValidator:
    """Validates resources before they are ingested into the catalog."""

    def validate(self, resources: List[CanonicalResource]) -> List[CanonicalResource]:
        """Validates all incoming resources, discarding invalid ones."""
        valid_resources = []
        for res in resources:
            try:
                # E.g., strict Pydantic checks would happen implicitly,
                # but here we can enforce business logic constraints
                if not res.resource_id:
                    raise ValueError("Missing resource_id")
                if not res.provider:
                    raise ValueError("Missing provider")
                
                valid_resources.append(res)
            except Exception as exc:
                logger.error("Catalog validation failed for resource: %s", exc)
                
        return valid_resources
