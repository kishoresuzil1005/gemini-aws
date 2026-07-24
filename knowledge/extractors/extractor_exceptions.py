# knowledge/extractors/extractor_exceptions.py
"""Custom exceptions for the Extractor Engine."""

class ExtractorError(Exception):
    """Base exception for extraction issues."""
    pass

class UnsupportedSourceError(ExtractorError):
    """Raised when no extractor is registered for a given context/source."""
    pass

class PartialExtractionError(ExtractorError):
    """Raised when extraction partially succeeds but some entities failed."""
    pass
