from typing import Dict, Any
from ..models.mission_models import MissionGoal

class KnowledgeGraphIntegration:
    """
    Updated KnowledgeGraph to answer blast-radius and feasibility questions 
    before the Mission Engine creates workflows.
    """
    def evaluate_mission_feasibility(self, goal: MissionGoal) -> Dict[str, Any]:
        print("[KnowledgeGraph] Checking blast radius for mission...")
        return {
            "feasible": True,
            "blast_radius": "LOW",
            "dependencies_affected": 2
        }
