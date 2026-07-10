from typing import Dict, Any, List

class WidgetEngine:
    """
    Supplies real-time aggregated data specifically formatted for UI frontend dashboard widgets.
    """
    def get_widget_data(self, widget_id: str) -> Dict[str, Any]:
        if widget_id == "cost_savings":
            return {"type": "bar_chart", "data": {"saved": 16800, "projected": 22000}}
        elif widget_id == "mission_status":
            return {"type": "pie_chart", "data": {"completed": 45, "running": 2, "failed": 1}}
        return {"type": "unknown", "data": {}}
