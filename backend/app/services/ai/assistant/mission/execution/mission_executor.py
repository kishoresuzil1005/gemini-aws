import asyncio
from ..core.mission_manager import MissionManager
from ..models.mission_models import MissionStatus

class MissionExecutor:
    """
    Executes the planned workflows for a mission asynchronously.
    Acts as the bridge between Mission Control and the Workflow Engine.
    """
    def __init__(self, manager: MissionManager):
        self.manager = manager

    def execute_async(self, mission_id: str):
        # In real code, push to a background worker queue (Celery/RabbitMQ)
        asyncio.create_task(self._run_mission(mission_id))

    async def _run_mission(self, mission_id: str):
        mission = self.manager.get_mission(mission_id)
        if not mission:
            return
            
        print(f"[MissionExecutor] Starting execution for mission: {mission_id}")
        self.manager.update_status(mission_id, MissionStatus.RUNNING)
        
        # Iterates through objectives, spawns workflows via Workflow Engine...
        # Mocking completion for this skeleton
        await asyncio.sleep(2)
        
        print(f"[MissionExecutor] Completed mission: {mission_id}")
        self.manager.update_status(mission_id, MissionStatus.COMPLETED