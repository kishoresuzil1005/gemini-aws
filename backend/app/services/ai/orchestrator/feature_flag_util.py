import yaml
from pathlib import Path

_feature_flags_path = Path(__file__).resolve().parents[4] / "feature_flags.yaml"

def is_enabled(flag_name: str) -> bool:
    if not _feature_flags_path.exists():
        return False
    with open(_feature_flags_path, "r") as f:
        data = yaml.safe_load(f) or {}
    return data.get(flag_name, False)
