from typing import Dict, Any
from ..core.mission_engine import MissionEngine

class GraphAssistant:
    """
    Updated GraphAssistant that now routes long-running intents to the MissionEngine 
    instead of directly to a single-task Planner.
    """
    def __init__(self, mission_engine: MissionEngine):
        self.mission_engine = mission_engine

    def handle_user_request(self, user_intent: str, context: Dict[str, Any]) -> str:
        # Determine if it's a mission or a simple task. Assume mission for now.
        if "reduce" in user_intent.lower() or "improve" in user_intent.lower() or "mission" in user_intent.lower():
            print("[GraphAssistant] Routing complex goal to Mission Engine...")
            mission_id = self.mission_engine.start_mission(user_intent, context)
            return f"Mission started with ID: {mission_id}"
        else:
            # Fallback to single-task Planner
            return "Simple task executed."