# knowledge/validation/schema_validator.py
"""Validator for JSON syntax and canonical schemas."""

import json
from typing import List

from .base_validator import BaseValidator
from .validation_models import SnapshotContext
from .validation_result import ValidationCheckResult
from .validation_exceptions import IntegrityError

class SchemaValidator(BaseValidator):
    def validate(self, context: SnapshotContext) -> List[ValidationCheckResult]:
        results = []
        
        # 1. JSON Syntax Validation (implicitly handles integrity of content)
        try:
            # For massive files, we'd use ijson, but json.loads is fine for this demo
            parsed = json.loads(context.raw_content)
            context.parsed_content = parsed
            results.append(ValidationCheckResult(
                validator_name=self.name, passed=True
            ))
        except json.JSONDecodeError as exc:
            raise IntegrityError(f"Snapshot content is not valid JSON: {exc}")

        # 2. Structure Validation (stubbed for canonical model mapping)
        # In a full implementation, we'd look up the Pydantic schema based on context.connector_name
        # and parse the content.
        
        if not isinstance(parsed, (dict, list)):
            results.append(ValidationCheckResult(
                validator_name=self.name, 
                passed=False, 
                errors=["Root of JSON must be an object or array"]
            ))
        else:
            results.append(ValidationCheckResult(
                validator_name=self.name, passed=True
            ))
            
        return results
