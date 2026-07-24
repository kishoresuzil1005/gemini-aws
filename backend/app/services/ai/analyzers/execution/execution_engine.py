"""
The core Analyzer Execution Engine.
"""
import logging
from typing import List, Dict, Any
from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.registry.analyzer_registry import AnalyzerRegistry
from app.services.ai.analyzers.execution.execution_context import ExecutionContext
from app.services.ai.analyzers.execution.execution_result import ExecutionResult
from app.services.ai.analyzers.execution.executors.base_executor import BaseExecutor
from app.services.ai.analyzers.execution.executors.sequential_executor import SequentialExecutor

logger = logging.getLogger(__name__)


class AnalyzerExecutionEngine:
    """
    Orchestrates the execution of multiple Analyzers.
    Resolves analyzer IDs from the registry and delegates execution
    to the configured ExecutionStrategy (Executor).
    """

    def __init__(self, registry: AnalyzerRegistry, executor: BaseExecutor = None):
        self.registry = registry
        self.executor = executor or SequentialExecutor()

    def execute(self, analyzer_ids: List[str], context: ExecutionContext, raw_context: Dict[str, Any]) -> ExecutionResult:
        """
        Executes a batch of analyzers by ID.
        
        Args:
            analyzer_ids (List[str]): The IDs of analyzers to execute.
            context (ExecutionContext): Tracing and metadata context.
            raw_context (Dict[str, Any]): Raw graph data.
            
        Returns:
            ExecutionResult: The aggregated result.
        """
        logger.info(f"[{context.request_id}] ExecutionEngine starting with {len(analyzer_ids)} analyzers.")
        
        resolved_analyzers: List[BaseAnalyzer] = []
        for a_id in analyzer_ids:
            analyzer = self.registry.get(a_id)
            if analyzer:
                resolved_analyzers.append(analyzer)
            else:
                logger.warning(f"[{context.request_id}] Analyzer {a_id} not found in registry. Skipping.")
                
        # Delegate to the strategy
        result = self.executor.execute(resolved_analyzers, context, raw_context)
        
        logger.info(
            f"[{context.request_id}] ExecutionEngine finished. "
            f"Success: {len(result.successful)}, Failed: {len(result.failed)}, "
            f"Skipped: {len(result.skipped)}, Time: {result.execution_time:.2f}s"
        )
        return result
