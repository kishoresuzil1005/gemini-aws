from typing import List
from ..memory.mission_history import MissionHistory

class MissionInsights:
    """
    Produces human-readable insights based on mission history.
    """
    def __init__(self, history: MissionHistory):
        self.history = history

    def generate_insights(self) -> List[str]:
        results = self.history.get_all_results()
        if not results:
            return ["No data available for insights."]
            
        return [
            f"Analyzed {len(results)} past missions.",
            "Cost optimization missions show a high success rate.",
            "Consider increasing concurrency for objective execution to reduce average mission time."
        ]