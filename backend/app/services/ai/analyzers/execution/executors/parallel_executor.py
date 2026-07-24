"""
Implements a parallel execution strategy using thread pools.
"""
import time
import logging
import concurrent.futures
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from app.services.ai.analyzers.base.base_analyzer import BaseAnalyzer
from app.services.ai.analyzers.execution.execution_context import ExecutionContext
from app.services.ai.analyzers.execution.execution_result import ExecutionResult
from app.services.ai.analyzers.execution.execution_metrics import ExecutionMetrics
from app.services.ai.analyzers.execution.executors.base_executor import BaseExecutor

logger = logging.getLogger(__name__)


class ParallelExecutor(BaseExecutor):
    """
    Executes analyzers concurrently using a ThreadPoolExecutor.
    """

    def __init__(self, max_workers: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.max_workers = max_workers

    def _execute_single(self, analyzer: BaseAnalyzer, context: ExecutionContext, raw_context: Dict[str, Any]) -> Tuple[str, Any, ExecutionMetrics, Optional[str]]:
        """Worker function for single analyzer execution using safe lifecycle hook."""
        analyzer_id = analyzer.metadata.id
        metrics = ExecutionMetrics(analyzer_name=analyzer_id, start_time=datetime.utcnow())
        analyzer_start = time.time()
        
        success, res, error = self._safe_lifecycle_execution(analyzer, raw_context)
        
        metrics.success = success
        metrics.execution_time = time.time() - analyzer_start
        metrics.end_time = datetime.utcnow()
        
        return analyzer_id, res, metrics, error

    def execute(self, analyzers: List[BaseAnalyzer], context: ExecutionContext, raw_context: Dict[str, Any]) -> ExecutionResult:
        start_time = time.time()
        result = ExecutionResult(executor=self.__class__.__name__)
        
        futures_map = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for analyzer in analyzers:
                future = executor.submit(self._execute_single, analyzer, context, raw_context)
                futures_map[future] = analyzer.metadata.id
                result.execution_order.append(analyzer.metadata.id)
                
            for future in concurrent.futures.as_completed(futures_map):
                analyzer_id = futures_map[future]
                try:
                    res_id, analyzer_res, metrics, error = future.result(timeout=self.timeout_policy.per_analyzer_timeout_seconds)
                    result.metrics[res_id] = metrics
                    
                    if error == "Validation failed":
                        result.skipped.append(res_id)
                        result.warnings.append(f"{res_id} skipped due to validation failure.")
                    elif error:
                        result.failed.append(res_id)
                        result.errors[res_id] = error
                        logger.error(f"[{context.request_id}] Analyzer {res_id} failed: {error}")
                    else:
                        result.successful.append(res_id)
                        result.results[res_id] = analyzer_res
                        
                except concurrent.futures.TimeoutError:
                    logger.error(f"[{context.request_id}] Analyzer {analyzer_id} timed out.")
                    result.failed.append(analyzer_id)
                    result.errors[analyzer_id] = "TimeoutException"
                except Exception as e:
                    logger.error(f"[{context.request_id}] Executor crashed on {analyzer_id}: {str(e)}")
                    result.failed.append(analyzer_id)
                    result.errors[analyzer_id] = str(e)
                    
        result.execution_time = time.time() - start_time
        return result
