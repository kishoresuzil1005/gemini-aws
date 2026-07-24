"""
Base interface for all Analyzers in the Enterprise Framework.
Provides safe default lifecycle methods to prevent boilerplate in stateless analyzers.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union
from app.services.ai.analyzers.base.analyzer_models import (
    AnalyzerResult, AnalyzerMetadata, CloudProvider, SupportedResource,
    AnalyzerContext, ValidationResult, AnalyzerStatus
)


class BaseAnalyzer(ABC):
    """
    Abstract base class for all Analyzers.
    
    Analyzers perform deterministic reasoning on given context
    and produce strongly-typed AnalyzerResults.
    """

    @property
    @abstractmethod
    def metadata(self) -> AnalyzerMetadata:
        """
        Returns the canonical metadata describing this analyzer.
        Must be implemented by all subclasses.
        
        Returns:
            AnalyzerMetadata: Strongly typed metadata.
        """
        pass

    def initialize(self) -> None:
        """
        Lifecycle hook for setup (e.g., opening database connections).
        Safe default: no-op.
        """
        pass

    def cleanup(self) -> None:
        """
        Lifecycle hook for teardown (e.g., closing connections).
        Safe default: no-op.
        """
        pass

    def health(self) -> bool:
        """
        Checks if the analyzer's dependencies are healthy and reachable.
        Safe default: returns True.
        
        Returns:
            bool: True if healthy.
        """
        return True

    def supports(self, cloud: CloudProvider, resource: SupportedResource) -> bool:
        """
        Checks if the analyzer supports a specific cloud and resource at runtime.
        Safe default: checks against the static metadata lists.
        
        Args:
            cloud (CloudProvider): Target cloud environment.
            resource (SupportedResource): Target resource type.
            
        Returns:
            bool: True if supported.
        """
        metadata = self.metadata
        return cloud in metadata.supported_clouds and resource in metadata.supported_resources

    def version(self) -> str:
        """
        Returns the semantic version of this analyzer.
        Safe default: returns the version from metadata.
        """
        return self.metadata.version

    def _coerce_context(self, context: Union[AnalyzerContext, Dict[str, Any]]) -> AnalyzerContext:
        """
        Internal helper to safely coerce legacy Dict context into a strongly-typed AnalyzerContext.
        """
        if isinstance(context, AnalyzerContext):
            return context
        return AnalyzerContext(
            graph=context.get("graph"),
            inventory=context.get("inventory"),
            metrics=context.get("metrics"),
            policies=context.get("policies"),
            topology=context.get("topology"),
            relationships=context.get("relationships"),
            execution_context=context.get("execution_context"),
            previous_results=context.get("previous_results")
        )

    def validate(self, context: Union[AnalyzerContext, Dict[str, Any]]) -> bool:
        """
        Validates if the provided context contains the necessary data for this analyzer.
        
        Args:
            context (Union[AnalyzerContext, Dict[str, Any]]): The typed context or raw dict.
            
        Returns:
            bool: True if validation passes, False otherwise.
        """
        # Safe default: assumes context is valid
        return True

    @abstractmethod
    def analyze(self, context: Union[AnalyzerContext, Dict[str, Any]]) -> AnalyzerResult:
        """
        Executes the core analysis logic.
        
        Args:
            context (Union[AnalyzerContext, Dict[str, Any]]): The typed context or raw dict.
            
        Returns:
            AnalyzerResult: The structured findings, recommendations, and score.
            
        Raises:
            AnalyzerExecutionException: If an error occurs during execution.
            NotImplementedError: If the analyzer is a placeholder.
        """
        pass

    def calculate_score(self, result: AnalyzerResult) -> int:
        """
        Calculates a priority/health score (0-100) based on the findings.
        Safe default: base 100, subtract 20 per critical, 10 per high, 5 per medium.
        
        Args:
            result (AnalyzerResult): The current analyzer result.
            
        Returns:
            int: The calculated score.
        """
        score = 100
        for finding in result.findings:
            severity = finding.severity.name if hasattr(finding.severity, "name") else str(finding.severity)
            if severity == "CRITICAL":
                score -= 20
            elif severity == "HIGH":
                score -= 10
            elif severity == "MEDIUM":
                score -= 5
            elif severity == "LOW":
                score -= 1
                
        return max(0, min(100, score))
