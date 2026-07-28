import time
from typing import Dict, Any
from contextvars import ContextVar

class MetricsTracker:
    def __init__(self):
        self.metrics: Dict[str, Dict[str, Any]] = {}

    def start(self, name: str) -> None:
        self.metrics[name] = {"start": time.time()}

    def finish(self, name: str) -> None:
        if name in self.metrics and "start" in self.metrics[name]:
            finish = time.time()
            self.metrics[name]["finish"] = finish
            self.metrics[name]["duration_ms"] = int((finish - self.metrics[name]["start"]) * 1000)

    def record(self, name: str, start: float, finish: float) -> None:
        self.metrics[name] = {
            "start": start,
            "finish": finish,
            "duration_ms": int((finish - start) * 1000)
        }

    def get_summary(self) -> Dict[str, Dict[str, Any]]:
        return self.metrics

    def clear(self) -> None:
        self.metrics.clear()

_metrics_ctx_var: ContextVar[MetricsTracker] = ContextVar("metrics_tracker")

def get_metrics_tracker() -> MetricsTracker:
    try:
        tracker = _metrics_ctx_var.get()
    except LookupError:
        tracker = MetricsTracker()
        _metrics_ctx_var.set(tracker)
    return tracker
