"""
Defines the base interface for Execution Strategies.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.execution.execution_context import ExecutionContext
from app.services.ai.analyzers.execution.execution_result import ExecutionResult
from app.services.ai.analyzers.execution.policies.retry_policy import RetryPolicy
from app.services.ai.analyzers.execution.policies.timeout_policy import TimeoutPolicy
from app.services.ai.analyzers.base.exceptions import AnalyzerInitializationException

logger = logging.getLogger(__name__)


class BaseExecutor(ABC):
    """
    Abstract strategy for executing a list of analyzers.
    Provides safety wrappers for the analyzer lifecycle.
    """

    def __init__(self, retry_policy: RetryPolicy = None, timeout_policy: TimeoutPolicy = None):
        self.retry_policy = retry_policy or RetryPolicy()
        self.timeout_policy = timeout_policy or TimeoutPolicy()

    def _safe_lifecycle_execution(self, analyzer: BaseAnalyzer, raw_context: Dict[str, Any]) -> Tuple[bool, Any, Optional[str]]:
        """
        Safely wraps the execution of an analyzer with initialize() and cleanup() hooks.
        
        Returns:
            Tuple[bool, Any, Optional[str]]: (Success, Result, ErrorMessage)
        """
        try:
            analyzer.initialize()
        except Exception as e:
            return False, None, f"Initialization failed: {str(e)}"
            
        try:
            # Re-check health in case initialize failed silently or dependency is down
            if not analyzer.health():
                return False, None, "Health check failed."
                
            if not analyzer.validate(raw_context):
                return False, None, "Validation failed"
                
            result = analyzer.analyze(raw_context)
            return True, result, None
            
        except Exception as e:
            return False, None, str(e)
            
        finally:
            try:
                analyzer.cleanup()
            except Exception as e:
                logger.error(f"Cleanup failed for {analyzer.metadata.id}: {str(e)}")

    @abstractmethod
    def execute(self, analyzers: List[BaseAnalyzer], context: ExecutionContext, raw_context: Dict[str, Any]) -> ExecutionResult:
        """Executes the provided analyzers."""
        pass
