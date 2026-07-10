from typing import Dict, Any

class PerformanceMonitor:
    """
    Tracks and analyzes the performance metrics of the multi-agent system (e.g. task completion times).
    """
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_completion_time_ms": 0.0,
        }

    def record_task_completion(self, duration_ms: float, success: bool):
        if success:
            total = self.metrics["tasks_completed"]
            current_avg = self.metrics["average_completion_time_ms"]
            self.metrics["average_completion_time_ms"] = ((current_avg * total) + duration_ms) / (total + 1)
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
