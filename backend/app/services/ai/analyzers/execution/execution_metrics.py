"""
Defines Execution Metrics for observability.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ExecutionMetrics(BaseModel):
    """
    Stores metrics about a specific analyzer's execution.
    Contains absolutely no business logic.
    """
    analyzer_name: str = Field(..., description="ID/name of the executed analyzer.")
    success: bool = Field(default=False, description="Whether the execution completed successfully.")
    
    start_time: datetime = Field(default_factory=datetime.utcnow, description="Execution start timestamp.")
    end_time: Optional[datetime] = Field(default=None, description="Execution end timestamp.")
    execution_time: float = Field(default=0.0, description="Total execution duration in seconds.")
    
    retry_count: int = Field(default=0, description="Number of times the execution was retried.")
    timeout: bool = Field(default=False, description="True if the analyzer timed out.")
    cache_hit: bool = Field(default=False, description="True if the result was served from cache.")
    
    resource_count: int = Field(default=0, description="Number of resources analyzed (if applicable).")
