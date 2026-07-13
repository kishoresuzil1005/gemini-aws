from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class LlmResponseData(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class StandardLlmResponse(BaseModel):
    status: str
    data: Optional[LlmResponseData] = None
    errors: List[Dict[str, Any]] = []

    @classmethod
    def success(cls, content: str, metadata: Dict[str, Any] = None):
        return cls(
            status="success",
            data=LlmResponseData(content=content, metadata=metadata or {})
        )

    @classmethod
    def error(cls, code: str, message: str, retryable: bool = False):
        return cls(
            status="error",
            errors=[{"code": code, "message": message, "retryable": retryable}]
        )