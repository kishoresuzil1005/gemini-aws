import logging

logger = logging.getLogger(__name__)

class GraphEventEngine:
    """
    Connects directly to the global Platform Event Bus.
    """
    def __init__(self, platform_event_bus):
        self.bus = platform_event_bus

    def publish(self, event_type: str, payload: dict):
        logger.info(f"Publishing Graph Event to Platform Bus: {event_type}")
        self.bus.publish(f"graph.{event_type}", payload)