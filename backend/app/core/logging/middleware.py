import uuid
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .request_id import set_request_id, get_request_id
from .context import set_module, set_stage, clear_context
from .logger import get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        clear_context()
        
        req_id = request.headers.get("X-Request-ID")
        if not req_id:
            req_id = f"req-{uuid.uuid4().hex[:8]}"
            
        set_request_id(req_id)
        set_module("API")
        set_stage("Request")
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            
            logger.info(
                f"{request.method} {request.url.path}\n\nStatus: {response.status_code}\nLatency: {process_time:.2f} ms\nRequest ID: {req_id}",
                extra={"status": "SUCCESS", "duration_ms": int(process_time)}
            )
            
            response.headers["X-Request-ID"] = req_id
            return response
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} failed",
                exc_info=True,
                extra={"status": "FAILED", "duration_ms": int(process_time)}
            )
            raise
