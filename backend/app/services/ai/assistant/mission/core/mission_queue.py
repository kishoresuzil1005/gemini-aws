import heapq
from typing import List, Optional
from ..models.mission_models import Mission, MissionPriority

class MissionQueue:
    """
    Priority Queue supporting CRITICAL, HIGH, MEDIUM, LOW, and BACKGROUND.
    Enables preemption of lower priority missions.
    """
    def __init__(self):
        # Priority Queue implemented using a heap. (priority_score, insertion_order, mission_id)
        self._queue = []
        self._counter = 0
        self._priority_map = {
            MissionPriority.CRITICAL: 1,
            MissionPriority.HIGH: 2,
            MissionPriority.MEDIUM: 3,
            MissionPriority.LOW: 4
        }
        self._active_missions = set()

    def enqueue(self, mission: Mission):
        priority = self._priority_map.get(mission.priority, 5) # 5 for Background/Unknown
        heapq.heappush(self._queue, (priority, self._counter, mission.mission_id))
        self._counter += 1

    def dequeue(self) -> Optional[str]:
        if not self._queue:
            return None
        _, _, mission_id = heapq.heappop(self._queue)
        self._active_missions.add(mission_id)
        return mission_id

    def peek(self) -> Optional[str]:
        if not self._queue:
            return None
        return self._queue[0][2]

    def is_empty(self) -> bool:
        return len(self._queue) == ""