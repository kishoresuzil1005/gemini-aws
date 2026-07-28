# knowledge/processing/parsers/json_parser.py
"""JSON Parser implementation."""

import json
from typing import Any

from .base_parser import BaseParser


class JsonParser(BaseParser):
    """Parses JSON format into standard Python structures."""

    def parse(self, raw_data: bytes, **kwargs) -> Any:
        try:
            return json.loads(raw_data.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse JSON: {exc}")
