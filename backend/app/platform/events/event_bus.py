from typing import Dict, Any, List, Callable
from datetime import datetime

class PlatformEvent:
    def __init__(self, topic: str, payload: Dict[str, Any], tenant_id: str):
        self.topic = topic
        self.payload = payload
        self.tenant_id = tenant_id
        self.timestamp = datetime.utcnow()

class EventBus:
    """
    Platform-wide event bus replacing local pub-sub. In production, this wraps Kafka or Redis PubSub.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, handler: Callable[[PlatformEvent], None]):
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(handler)

    def publish(self, event: PlatformEvent):
        print(f"[EventBus] Publishing {event.topic} for tenant {event.tenant_id}")
        if event.topic in self.subscribers:
            for handler in self.subscribers[event.topic]:
                handler(event)
