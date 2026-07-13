import uuid
from typing import Dict, Any

class ProviderContext:
    """Passes context (request ID, timeout, etc.) down through provider calls."""
    def __init__(self, request_id: str = None, timeout: int = 30):
        self.request_id = request_id or str(uuid.uuid4())
        self.timeout = timeout
        self.state: Dict[str, Any] = {}
