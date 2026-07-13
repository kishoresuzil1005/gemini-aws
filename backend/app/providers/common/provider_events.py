from typing import Dict, Any

class ProviderEventBus:
    """Publishes events emitted by the provider layer to the platform."""
    def publish(self, event_type: str, payload: Dict[str, Any]):
        # e.g., send to Kafka, Redis PubSub, or in-memory queue
        print(f"[EVENT] {event_type}: {payload}")

provider_event_bus = ProviderEventBus()
