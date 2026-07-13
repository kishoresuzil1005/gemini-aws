from typing import Dict, Any
from ..core.mission_manager import MissionManager
from ..analytics.mission_metrics import MissionMetrics
from ..models.mission_models import MissionStatus

class MissionDashboard:
    """
    Provides a live operational view of the Mission Control layer.
    Can be exposed via API to a frontend dashboard.
    """
    def __init__(self, manager: MissionManager, metrics: MissionMetrics):
        self.manager = manager
        self.metrics = metrics

    def get_dashboard_summary(self) -> Dict[str, Any]:
        missions = self.manager.repository.get_all()
        
        running = sum(1 for m in missions if m.status == MissionStatus.RUNNING)
        completed = sum(1 for m in missions if m.status == MissionStatus.COMPLETED)
        failed = sum(1 for m in missions if m.status == MissionStatus.FAILED)
        paused = sum(1 for m in missions if m.status == MissionStatus.PAUSED)
        
        historical_metrics = self.metrics.calculate_metrics()
        
        # In a real scenario, average cost saved and rollback counts would be pulled from actual billing APIs and event stores
        return {
            "active_status": {
                "running": running,
                "completed": completed,
                "failed": failed,
                "paused": paused
            },
            "performance": {
                "average_completion_time_sec": historical_metrics.get("average_duration_sec", 0),
                "success_rate_pct": historical_metrics.get("success_rate_pct", 0)
            },
            "business_impact": {
                "average_cost_saved": "$380/month", # Mocked
                "rollback_count": 0 # Mocked
            },
            "recent_missions": [
                {"id": m.mission_id, "title": m.title, "status": m.status.value}
                for m in missions[-5:]
            ]
        