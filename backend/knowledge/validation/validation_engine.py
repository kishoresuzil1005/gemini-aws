# knowledge/validation/validation_engine.py
"""The Validation Engine orchestrates the execution of the validation pipeline."""

import logging
import uuid
import time
from typing import List

from .validation_models import SnapshotContext
from .validation_registry import ValidationRegistry
from .validation_report import ValidationReport, ValidationReportChecks, ValidationWarning
from .validation_exceptions import FatalValidationError, IntegrityError

logger = logging.getLogger(__name__)


class ValidationEngine:
    """Provider-independent engine that orchestrates snapshot validation."""

    def __init__(self):
        self.registry = ValidationRegistry()
        self.pipeline = self.registry.get_pipeline()

    def validate_snapshot(self, context: SnapshotContext) -> ValidationReport:
        """Run the full validation pipeline against a SnapshotContext."""
        start_time = time.time()
        
        report = ValidationReport(
            validation_id=str(uuid.uuid4()),
            snapshot_id=f"{context.connector_name}-{context.metadata.get('timestamp', 'unknown')}",
            provider=context.provider,
            knowledge_source=context.connector_name,
            status="PENDING"
        )
        
        try:
            for validator in self.pipeline:
                logger.debug("Executing %s", validator.name)
                
                try:
                    results = validator.validate(context)
                except FatalValidationError as exc:
                    logger.error("Fatal validation error in %s: %s", validator.name, exc)
                    report.status = "REJECTED"
                    report.errors.append(f"Fatal error in {validator.name}: {exc}")
                    break
                except Exception as exc:
                    logger.exception("Unexpected error in %s: %s", validator.name, exc)
                    report.status = "REJECTED"
                    report.errors.append(f"Unexpected error in {validator.name}: {exc}")
                    break
                    
                for result in results:
                    report.detailed_results.append(result)
                    
                    if result.metric_name == "quality_score" and result.metric_value is not None:
                        report.quality_score = result.metric_value
                        
                    if result.passed:
                        report.checks.passed += 1
                        if result.warnings:
                            report.checks.warnings += len(result.warnings)
                            for w in result.warnings:
                                report.warnings.append(ValidationWarning(validator=validator.name, message=w))
                    else:
                        report.checks.failed += 1
                        report.status = "REJECTED"
                        for err in result.errors:
                            report.errors.append(f"[{validator.name}] {err}")

            if report.status == "PENDING":
                report.status = "PASSED" if report.checks.failed == 0 else "REJECTED"
                
        finally:
            report.duration_ms = int((time.time() - start_time) * 1000)
            
        logger.info(
            "Validation finished for %s. Status: %s. Passed: %d, Failed: %d, Duration: %d ms",
            report.snapshot_id, report.status, report.checks.passed, report.checks.failed, report.duration_ms
        )
        return report
