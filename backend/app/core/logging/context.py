from contextvars import ContextVar
from typing import Optional

_module_ctx_var: ContextVar[Optional[str]] = ContextVar("module", default=None)
_stage_ctx_var: ContextVar[Optional[str]] = ContextVar("stage", default=None)
_service_ctx_var: ContextVar[str] = ContextVar("service", default="CloudOps")

def set_module(module: str) -> None:
    _module_ctx_var.set(module)

def get_module() -> Optional[str]:
    return _module_ctx_var.get()

def set_stage(stage: str) -> None:
    _stage_ctx_var.set(stage)

def get_stage() -> Optional[str]:
    return _stage_ctx_var.get()

def set_service(service: str) -> None:
    _service_ctx_var.set(service)

def get_service() -> str:
    return _service_ctx_var.get()

def clear_context() -> None:
    _module_ctx_var.set(None)
    _stage_ctx_var.set(None)
