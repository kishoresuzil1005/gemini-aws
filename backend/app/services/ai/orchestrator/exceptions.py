"""Custom exceptions for the AI Context Orchestrator."""


class OrchestratorError(Exception):
    """Base orchestrator error."""


class ProviderError(OrchestratorError):
    """Raised when a context provider fails."""

    def __init__(self, provider_name: str, reason: str):
        self.provider_name = provider_name
        self.reason = reason
        super().__init__(f"[{provider_name}] {reason}")


class ResolutionError(OrchestratorError):
    """Raised when resource resolution fails."""


class ValidationError(OrchestratorError):
    """Raised when context validation fails."""


class BudgetExceededError(OrchestratorError):
    """Raised when prompt token budget is exceeded."""


class FeatureFlagDisabledError(OrchestratorError):
    """Raised when accessing a feature that is disabled via flag."""


class InvestigationError(OrchestratorError):
    """Raised during investigation session errors."""


class PolicyViolationError(OrchestratorError):
    """Raised when a remediation plan violates policy guardrails."""
