# knowledge/validation/base_validator.py
"""Abstract base class for all validation rules."""

import abc
import logging
from typing import List

from .validation_models import SnapshotContext
from .validation_result import ValidationCheckResult
from .validation_exceptions import FatalValidationError

logger = logging.getLogger(__name__)


class BaseValidator(abc.ABC):
    """Base class for all validators in the pipeline.
    
    Validators must be stateless, thread-safe, and deterministic.
    """

    def __init__(self):
        self.name = self.__class__.__name__

    @abc.abstractmethod
    def validate(self, context: SnapshotContext) -> List[ValidationCheckResult]:
        """Execute the validation logic against the given snapshot context.
        
        Returns a list of validation results. May raise FatalValidationError if 
        the error should halt the pipeline entirely.
        """
        raise NotImplementedError
