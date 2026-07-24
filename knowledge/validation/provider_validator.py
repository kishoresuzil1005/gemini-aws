# knowledge/validation/provider_validator.py
"""Validator for provider taxonomy and known services."""

from typing import List

from .base_validator import BaseValidator
from .validation_models import SnapshotContext
from .validation_result import ValidationCheckResult


class ProviderValidator(BaseValidator):
    def validate(self, context: SnapshotContext) -> List[ValidationCheckResult]:
        results = []
        
        # Valid providers for the current architecture
        allowed_providers = ["aws"]
        
        if context.provider not in allowed_providers:
            results.append(ValidationCheckResult(
                validator_name=self.name,
                passed=False,
                errors=[f"Unknown provider '{context.provider}'. Allowed: {allowed_providers}"]
            ))
        else:
            results.append(ValidationCheckResult(validator_name=self.name, passed=True))
            
        return results
