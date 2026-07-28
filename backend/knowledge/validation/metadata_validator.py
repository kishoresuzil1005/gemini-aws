# knowledge/validation/metadata_validator.py
"""Validator for metadata completeness and standard formats."""

from typing import List
from datetime import datetime

from .base_validator import BaseValidator
from .validation_models import SnapshotContext
from .validation_result import ValidationCheckResult


class MetadataValidator(BaseValidator):
    def validate(self, context: SnapshotContext) -> List[ValidationCheckResult]:
        results = []
        meta = context.metadata
        
        # 1. Required fields
        required = ["connector", "version", "timestamp", "size_bytes", "checksum_sha256"]
        missing = [f for f in required if f not in meta]
        
        if missing:
            results.append(ValidationCheckResult(
                validator_name=self.name, passed=False, errors=[f"Missing metadata fields: {missing}"]
            ))
        else:
            results.append(ValidationCheckResult(validator_name=self.name, passed=True))
            
            # 2. Timestamp format
            ts = meta["timestamp"]
            try:
                # expecting ISO format ending in Z or +00:00
                ts_clean = ts.replace("Z", "+00:00")
                datetime.fromisoformat(ts_clean)
                results.append(ValidationCheckResult(validator_name=self.name, passed=True))
            except ValueError:
                results.append(ValidationCheckResult(
                    validator_name=self.name, passed=False, errors=[f"Invalid timestamp format: {ts}"]
                ))

        return results
