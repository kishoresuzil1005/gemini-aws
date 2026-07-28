import logging
import os
from .formatter import JSONFormatter

def setup_logger() -> None:
    log_level_str = os.environ.get("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level_str, logging.INFO)

    root_logger = logging.getLogger()
    
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)
    
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        l = logging.getLogger(logger_name)
        l.handlers = [handler]
        l.setLevel(numeric_level)
        l.propagate = False

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
