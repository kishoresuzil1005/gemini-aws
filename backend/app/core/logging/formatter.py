import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

from .request_id import get_request_id
from .context import get_module, get_stage, get_service

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        module = get_module() or getattr(record, "module", record.name)
        stage = get_stage() or getattr(record, "stage", None)
        
        log_obj: Dict[str, Any] = {
            "timestamp": timestamp,
            "request_id": get_request_id(),
            "level": record.levelname,
            "module": module,
            "function": record.funcName,
            "stage": stage,
            "status": getattr(record, "status", "SUCCESS" if record.levelno < logging.ERROR else "FAILED"),
            "duration_ms": getattr(record, "duration_ms", None),
            "service": get_service(),
            "thread": record.threadName,
            "message": record.getMessage()
        }

        # Remove None values
        log_obj = {k: v for k, v in log_obj.items() if v is not None}

        if record.exc_info:
            log_obj["exception"] = record.exc_info[0].__name__ if record.exc_info[0] else "UnknownException"
            log_obj["stack_trace"] = self.formatException(record.exc_info)
            
        if hasattr(record, "resource_id"):
            log_obj["resource_id"] = record.resource_id
            
        if hasattr(record, "user_id"):
            log_obj["user_id"] = record.user_id

        # Merge any other extra fields explicitly added via kwargs (if passed properly)
        if hasattr(record, "extra_fields"):
            for k, v in getattr(record, "extra_fields", {}).items():
                if k not in log_obj:
                    log_obj[k] = v

        return json.dumps(log_obj)
