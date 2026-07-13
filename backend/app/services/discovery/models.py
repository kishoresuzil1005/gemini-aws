from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ScanResult:
    scan_id: str
    account_id: Optional[str]
    regions: List[str]
    started_at: datetime
    finished_at: datetime
    duration: int
    resources: List[Dict[str, Any]]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)