from typing import List
from ..models.mission_models import MissionResult

class MissionHistory:
    """
    Stores the outcomes and logs of all historically completed or failed missions.
    """
    def __init__(self):
        self._history: List[MissionResult] = []

    def record_result(self, result: MissionResult):
        self._history.append(result)

    def get_all_results(self) -> List[MissionResult]:
        return self._history
