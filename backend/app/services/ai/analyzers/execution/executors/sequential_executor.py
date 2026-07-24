"""
Implements a sequential execution strategy.
"""
import time
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.execution.execution_context import ExecutionContext
from app.services.ai.analyzers.execution.execution_result import ExecutionResult
from app.services.ai.analyzers.execution.execution_metrics import ExecutionMetrics
from app.services.ai.analyzers.execution.executors.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


class SequentialExecutor(BaseExecutor):
    """
    Executes analyzers one by one sequentially in the current thread.
    Useful for simple tasks or debugging.
    """

    def execute(self, analyzers: List[BaseAnalyzer], context: ExecutionContext, raw_context: Dict[str, Any]) -> ExecutionResult:
        start_time = time.time()
        
        result = ExecutionResult(executor=self.__class__.__name__)
        
        for analyzer in analyzers:
            analyzer_id = analyzer.metadata.id
            result.execution_order.append(analyzer_id)
            metrics = ExecutionMetrics(analyzer_name=analyzer_id, start_time=datetime.utcnow())
            
            analyzer_start = time.time()
            
            # Delegate to the safe lifecycle wrapper in the base class
            success, analyzer_res, error = self._safe_lifecycle_execution(analyzer, raw_context)
            
            metrics.execution_time = time.time() - analyzer_start
            metrics.end_time = datetime.utcnow()
            
            if error == "Validation failed":
                result.skipped.append(analyzer_id)
                result.warnings.append(f"{analyzer_id} skipped due to validation failure.")
            elif error:
                result.failed.append(analyzer_id)
                result.errors[analyzer_id] = error
                metrics.success = False
                logger.error(f"[{context.request_id}] Analyzer {analyzer_id} failed: {error}")
            else:
                result.successful.append(analyzer_id)
                result.results[analyzer_id] = analyzer_res
                metrics.success = True
                
            result.metrics[analyzer_id] = metrics
                
        result.execution_time = time.time() - start_time
        return result
