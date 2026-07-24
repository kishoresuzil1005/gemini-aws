"""
Defines the Retry Policy for analyzer execution.
"""
from typing import List, Type
from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    """
    Defines how the executor should handle retries for transient failures.
    """
    max_attempts: int = Field(default=3, description="Maximum number of execution attempts.")
    backoff_multiplier: float = Field(default=2.0, description="Multiplier for exponential backoff.")
    initial_delay_seconds: float = Field(default=1.0, description="Initial delay between retries.")
    
    # We store exception names as strings to avoid tight coupling or import cycles
    retryable_exceptions: List[str] = Field(
        default_factory=lambda: ["AnalyzerExecutionException", "TimeoutError", "ConnectionError"],
        description="List of exception class names that trigger a retry."
    )
