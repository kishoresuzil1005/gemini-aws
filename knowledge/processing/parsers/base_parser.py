# knowledge/processing/parsers/base_parser.py
"""Abstract base class for all parsers in M5."""

import abc
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BaseParser(abc.ABC):
    """Base class for converting raw formats into an intermediate representation.
    
    The intermediate representation is typically a deeply nested Python dictionary
    or list, stripped of format-specific syntax but not yet mapped to a canonical schema.
    """

    def __init__(self):
        self.name = self.__class__.__name__

    @abc.abstractmethod
    def parse(self, raw_data: bytes, **kwargs) -> Any:
        """Parse raw bytes into an intermediate in-memory representation.
        
        Args:
            raw_data: The raw file contents.
            **kwargs: Additional hints (e.g., encoding, partial document boundaries).
            
        Returns:
            The parsed representation (e.g., dict, list, or AST).
        """
        raise NotImplementedError
