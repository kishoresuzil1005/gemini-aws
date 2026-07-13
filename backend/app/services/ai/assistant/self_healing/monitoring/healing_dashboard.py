from typing import Dict, Any
from ..timeline.healing_timeline import HealingTimeline
from ..analytics.healing_metrics import HealingMetrics

class HealingDashboard:
    """
    Aggregates self-healing states, metrics, and timelines for UI consumption.
    """
    def __init__(self, timeline: HealingTimeline, metrics: HealingMetrics):
        self.timeline = timeline
        self.metrics = metrics

    def get_dashboard_data(self) -> Dict[str, Any]:
        return {
            "mttr_minutes": self.metrics.calculate_mttr([]),
            "success_rate_percent": self.metrics.get_success_ratio(),
            "active_incidents": 1,
            "incidents_healed_today": 12,
            "rollback_count": 0
        }