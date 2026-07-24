"""
Defines the aggregate Execution Result returned by the engine.
"""
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from app.services.ai.analyzers.base.analyzer_models import AnalyzerResult
from app.services.ai.analyzers.execution.execution_metrics import ExecutionMetrics


class ExecutionResult(BaseModel):
    """
    Wraps the results of multiple analyzers executed by the engine.
    It tracks what succeeded, what failed, and aggregates metrics.
    """
    successful: List[str] = Field(default_factory=list, description="IDs of analyzers that succeeded.")
    failed: List[str] = Field(default_factory=list, description="IDs of analyzers that failed.")
    skipped: List[str] = Field(default_factory=list, description="IDs of analyzers that were skipped (e.g. timeout).")
    
    execution_time: float = Field(default=0.0, description="Total orchestration time in seconds.")
    
    results: Dict[str, AnalyzerResult] = Field(default_factory=dict, description="Map of analyzer ID to its result.")
    metrics: Dict[str, ExecutionMetrics] = Field(default_factory=dict, description="Map of analyzer ID to its metrics.")
    
    errors: Dict[str, str] = Field(default_factory=dict, description="Map of analyzer ID to error string.")
    warnings: List[str] = Field(default_factory=list, description="General warnings during execution.")
    
    execution_order: List[str] = Field(default_factory=list, description="The order in which analyzers were executed.")
    executor: str = Field(..., description="The name of the executor strategy used (e.g., SequentialExecutor).")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional orchestrator metadata.")
