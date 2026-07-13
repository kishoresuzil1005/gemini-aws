from ..models.mission_models import Mission
from .mission_serializer import MissionSerializer

class MissionExporter:
    """
    Exports a mission's state and context for backup or external reporting.
    """
    @staticmethod
    def export_to_file(mission: Mission, file_path: str):
        data = MissionSerializer.to_json(mission)
        with open(file_path, "w") as f:
            f.write(data