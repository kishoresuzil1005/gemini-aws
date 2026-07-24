"""
Defines the Timeout Policy for analyzer execution.
"""
from pydantic import BaseModel, Field


class TimeoutPolicy(BaseModel):
    """
    Defines how the executor should enforce timeouts on analyzers.
    """
    default_timeout_seconds: float = Field(default=30.0, description="Default timeout for overall execution.")
    per_analyzer_timeout_seconds: float = Field(default=10.0, description="Timeout for a single analyzer.")
    cancel_on_timeout: bool = Field(default=True, description="Whether to aggressively cancel the task on timeout.")
