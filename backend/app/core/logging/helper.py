import time
from typing import Optional, Dict, Any
from .logger import get_logger
from .context import set_stage

class LogHelper:
    @staticmethod
    def stage_start(stage_name: str, message: str = "", extra: Optional[Dict[str, Any]] = None) -> float:
        set_stage(stage_name)
        logger = get_logger("LogHelper")
        msg = message or f"{stage_name} Started"
        logger.info(msg, extra={"status": "STARTED", **(extra or {})})
        return time.time()

    @staticmethod
    def stage_finish(stage_name: str, start_time: float, message: str = "", extra: Optional[Dict[str, Any]] = None) -> None:
        duration = int((time.time() - start_time) * 1000)
        logger = get_logger("LogHelper")
        msg = message or f"{stage_name} Finished"
        logger.info(msg, extra={"status": "SUCCESS", "duration_ms": duration, **(extra or {})})

    @staticmethod
    def stage_error(stage_name: str, start_time: float, exception: Exception, message: str = "", extra: Optional[Dict[str, Any]] = None) -> None:
        duration = int((time.time() - start_time) * 1000)
        logger = get_logger("LogHelper")
        msg = message or f"{stage_name} Failed"
        logger.exception(msg, exc_info=exception, extra={"status": "FAILED", "duration_ms": duration, **(extra or {})})

    @staticmethod
    def summary(summary_title: str, data: Dict[str, Any]) -> None:
        logger = get_logger("LogHelper")
        
        lines = ["=" * 50, summary_title.upper(), "=" * 50]
        for k, v in data.items():
            lines.append(f"{k}")
            if isinstance(v, list):
                for item in v:
                    lines.append(f"{item}")
            else:
                lines.append(f"{v}")
            lines.append("")
        lines.append("=" * 50)
        
        msg = "\n".join(lines)
        logger.info(msg, extra={"summary_data": data})
