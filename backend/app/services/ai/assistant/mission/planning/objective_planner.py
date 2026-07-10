import uuid
from typing import List
from ..models.mission_models import MissionGoal, MissionObjective

class ObjectivePlanner:
    """
    Breaks down a single MissionGoal into sequential or parallel MissionObjectives.
    """
    def generate_objectives(self, goal: MissionGoal) -> List[MissionObjective]:
        print("[ObjectivePlanner] Generating objectives for goal...")
        # Mock logic
        obj1 = MissionObjective(
            objective_id=str(uuid.uuid4()),
            description="Identify and stop idle EC2 instances"
        )
        obj2 = MissionObjective(
            objective_id=str(uuid.uuid4()),
            description="Delete unattached EBS volumes",
            dependencies=[obj1.objective_id]
        )
        goal.objectives = [obj1, obj2]
        return goal.objectives
