"""
AI Context Orchestrator Package
=================================
Public surface — import from here, not from submodules.
"""

from .exceptions import (
    OrchestratorError,
    ProviderError,
    ResolutionError,
    ValidationError,
    BudgetExceededError,
    PolicyViolationError,
)
from .feature_flag_util import is_enabled
from .models import (
    CloudProvider,
    Resource,
    ResourceStatus,
    ResourceRelationship,
    SecurityFinding,
    MetricPoint,
    CandidateQuery,
    ResolvedResource,
    ReasoningResult,
    ProviderResult,
    ProviderOutcome,
    ProviderPriority,
    ContextQualityScore,
    UnifiedContext,
    IntentCategory,
)
from .provider_registry import ProviderRegistry, ProviderRegistration
from .aggregator import ContextAggregator
from .validator import ContextValidator, ValidationReport
from .budget_manager import BudgetManager
from .cache import OrchestratorCache
from .telemetry import (
    track_orchestrator_latency,
    track_provider_latency,
    record_cache_hit,
    record_cache_miss,
    record_resolution,
    record_llm_tokens,
)
from .orchestrator import Orchestrator

__all__ = [
    # Core
    "Orchestrator",
    "ProviderRegistry",
    "ProviderRegistration",
    # Models
    "CloudProvider",
    "Resource",
    "ResourceStatus",
    "ResourceRelationship",
    "SecurityFinding",
    "MetricPoint",
    "CandidateQuery",
    "ResolvedResource",
    "ReasoningResult",
    "ProviderResult",
    "ProviderOutcome",
    "ProviderPriority",
    "ContextQualityScore",
    "UnifiedContext",
    "IntentCategory",
    # Subsystems
    "ContextAggregator",
    "ContextValidator",
    "ValidationReport",
    "BudgetManager",
    "OrchestratorCache",
    # Exceptions
    "OrchestratorError",
    "ProviderError",
    "ResolutionError",
    "ValidationError",
    "BudgetExceededError",
    "PolicyViolationError",
    # Feature flags
    "is_enabled",
    # Telemetry
    "track_orchestrator_latency",
    "track_provider_latency",
    "record_cache_hit",
    "record_cache_miss",
    "record_resolution",
    "record_llm_tokens",
]
