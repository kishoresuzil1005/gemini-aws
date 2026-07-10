from typing import Dict, List, Optional
from ..models.mission_models import Mission

class MissionRepository:
    """
    Persistence layer for missions. Mocked as in-memory dict for now,
    but designed to be backed by PostgreSQL or MongoDB.
    """
    def __init__(self):
        self._store: Dict[str, Mission] = {}

    def save(self, mission: Mission):
        self._store[mission.mission_id] = mission

    def get(self, mission_id: str) -> Optional[Mission]:
        return self._store.get(mission_id)

    def get_all(self) -> List[Mission]:
        return list(self._store.values())
