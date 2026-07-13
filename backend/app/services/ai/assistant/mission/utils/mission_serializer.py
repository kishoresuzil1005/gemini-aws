import json
from ..models.mission_models import Mission

class MissionSerializer:
    """
    Serializes a Mission object into JSON and vice-versa.
    """
    @staticmethod
    def to_json(mission: Mission) -> str:
        return mission.model_dump_json()

    @staticmethod
    def from_json(json_str: str) -> Mission:
        return Mission.model_validate_json(json_str)