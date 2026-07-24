# knowledge/validation/validation_registry.py
"""Central registry for discovering and instantiating validation rules."""

from typing import List, Type

from .base_validator import BaseValidator
from .schema_validator import SchemaValidator
from .metadata_validator import MetadataValidator
from .relationship_validator import RelationshipValidator
from .version_validator import VersionValidator
from .provider_validator import ProviderValidator
from .duplicate_validator import DuplicateValidator
from .quality_validator import QualityValidator


class ValidationRegistry:
    """Manages the ordered collection of validators that make up the pipeline."""

    def __init__(self):
        # Order matters: Schema and Metadata should run before complex checks
        self._validators: List[Type[BaseValidator]] = [
            SchemaValidator,
            MetadataValidator,
            RelationshipValidator,
            VersionValidator,
            ProviderValidator,
            DuplicateValidator,
            QualityValidator,
        ]

    def get_pipeline(self) -> List[BaseValidator]:
        """Returns instantiated validators in execution order."""
        return [validator_cls() for validator_cls in self._validators]
