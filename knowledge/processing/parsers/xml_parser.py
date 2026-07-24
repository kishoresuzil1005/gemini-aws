# knowledge/processing/parsers/xml_parser.py
"""XML Parser implementation."""

import xml.etree.ElementTree as ET
from typing import Any, Dict

from .base_parser import BaseParser


class XmlParser(BaseParser):
    """Parses XML format into an intermediate dictionary structure."""

    def _elem_to_dict(self, elem: ET.Element) -> Dict[str, Any]:
        """Recursive helper to convert XML element to dictionary."""
        d = {elem.tag: {} if elem.attrib else None}
        children = list(elem)
        if children:
            dd = {}
            for dc in map(self._elem_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        if type(dd[k]) is list:
                            dd[k].append(v)
                        else:
                            dd[k] = [dd[k], v]
                    else:
                        dd[k] = v
            d = {elem.tag: dd}
        if elem.attrib:
            d[elem.tag].update(("@" + k, v) for k, v in elem.attrib.items())
        if elem.text:
            text = elem.text.strip()
            if children or elem.attrib:
                if text:
                    d[elem.tag]["#text"] = text
            else:
                d[elem.tag] = text
        return d

    def parse(self, raw_data: bytes, **kwargs) -> Any:
        try:
            root = ET.fromstring(raw_data)
            return self._elem_to_dict(root)
        except ET.ParseError as exc:
            raise ValueError(f"Failed to parse XML: {exc}")
