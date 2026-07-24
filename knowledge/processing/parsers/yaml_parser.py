# knowledge/processing/parsers/yaml_parser.py
"""YAML Parser implementation."""

import yaml
from typing import Any

from .base_parser import BaseParser


class YamlParser(BaseParser):
    """Parses YAML format into standard Python structures."""

    def parse(self, raw_data: bytes, **kwargs) -> Any:
        try:
            return yaml.safe_load(raw_data.decode("utf-8"))
        except yaml.YAMLError as exc:
            raise ValueError(f"Failed to parse YAML: {exc}")
