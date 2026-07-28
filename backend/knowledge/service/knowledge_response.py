# knowledge/service/knowledge_response.py
"""Response builder utility."""

import time
from typing import Any, Dict, Optional, List
from .knowledge_models import KnowledgeResponse, Pagination

class ResponseBuilder:
    """Helper to cleanly build standard responses."""
    
    @staticmethod
    def build(
        data: Any,
        start_time: float,
        metadata: Optional[Dict[str, Any]] = None,
        pagination: Optional[Pagination] = None,
        cache_hit: bool = False,
        errors: Optional[List[str]] = None
    ) -> KnowledgeResponse:
        duration = int((time.time() - start_time) * 1000)
        return KnowledgeResponse(
            data=data,
            metadata=metadata or {},
            pagination=pagination,
            cache_hit=cache_hit,
            duration_ms=duration,
            errors=errors or []
        )
