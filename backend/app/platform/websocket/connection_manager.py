from app.core.logging import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List

class WebSocketManager:
    """
    Manages live streaming updates for frontend dashboards.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[Any]] = {} # tenant_id -> List of WebSocket connections

    async def connect(self, tenant_id: str, websocket: Any):
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = []
        self.active_connections[tenant_id].append(websocket)
        logger.debug(f"[WebSocket] Connected tenant {tenant_id}")

    def disconnect(self, tenant_id: str, websocket: Any):
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].remove(websocket)

    async def broadcast_to_tenant(self, tenant_id: str, message: Dict[str, Any]):
        connections = self.active_connections.get(tenant_id, [])
        for conn in connections:
            try:
                # Mock send logic (await conn.send_json(message))
                logger.debug(f"[WebSocket] Streaming to {tenant_id}: {message}")
            except Exception as e:
                logger.debug(f"[WebSocket] Failed to stream: {e}")
                self.disconnect(tenant_id, conn)
