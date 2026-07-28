import uuid
from contextvars import ContextVar
from typing import Optional

_request_id_ctx_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

def set_request_id(request_id: str) -> None:
    _request_id_ctx_var.set(request_id)

def get_request_id() -> str:
    req_id = _request_id_ctx_var.get()
    if not req_id:
        req_id = f"req-{uuid.uuid4().hex[:8]}"
        _request_id_ctx_var.set(req_id)
    return req_id
