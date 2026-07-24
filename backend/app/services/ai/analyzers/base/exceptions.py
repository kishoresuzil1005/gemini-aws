"""
Comprehensive Exception Hierarchy for the Analyzer Framework.
"""

class AnalyzerException(Exception):
    """Base exception for all Analyzer Framework errors."""
    pass

class AnalyzerRegistrationException(AnalyzerException):
    """Raised when an analyzer fails to register (e.g., duplicate ID, invalid metadata)."""
    pass

class AnalyzerConfigurationException(AnalyzerException):
    """Raised when an analyzer is improperly configured or missing required secrets."""
    pass

class AnalyzerDependencyException(AnalyzerException):
    """Raised when an analyzer cannot run due to a missing or failed upstream analyzer."""
    pass

class AnalyzerInitializationException(AnalyzerException):
    """Raised when an analyzer fails during the initialize() lifecycle phase."""
    pass

class AnalyzerValidationException(AnalyzerException):
    """Raised when the context provided to an analyzer is fundamentally invalid."""
    pass

class AnalyzerExecutionException(AnalyzerException):
    """Raised when an analyzer encounters an unhandled error during analyze()."""
    pass

class AnalyzerTimeoutException(AnalyzerExecutionException):
    """Raised when an analyzer exceeds its allocated execution time."""
    pass

class AnalyzerHealthCheckException(AnalyzerException):
    """Raised when an analyzer reports unhealthy dependencies (e.g., database unreachable)."""
    pass

class AnalyzerPluginException(AnalyzerException):
    """Raised when dynamically loading an external analyzer plugin fails."""
    pass
