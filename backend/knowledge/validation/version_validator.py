# knowledge/validation/version_validator.py
"""Validator for composite version strings."""

from typing import List

from .base_validator import BaseValidator
from .validation_models import SnapshotContext
from .validation_result import ValidationCheckResult


class VersionValidator(BaseValidator):
    def validate(self, context: SnapshotContext) -> List[ValidationCheckResult]:
        results = []
        version_str = context.metadata.get("version", "")
        
        # We expect a composite version separated by pipes e.g., "1.0|api-v1" or similar
        parts = version_str.split("|")
        if len(parts) >= 2:
            results.append(ValidationCheckResult(validator_name=self.name, passed=True))
        else:
            results.append(ValidationCheckResult(
                validator_name=self.name, 
                passed=False,
                errors=[f"Version string '{version_str}' does not follow composite pattern (e.g. connector|source|snapshot)"]
            ))
            
        return results
