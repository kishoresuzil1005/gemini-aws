from typing import Dict, Callable, List
from ..base.base_message import EventMessage
import asyncio

class EventBus:
    def __init__(self):
        self.topic_subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[EventMessage], None]):
        if event_type not in self.topic_subscribers:
            self.topic_subscribers[event_type] = []
        self.topic_subscribers[event_type].append(callback)

    async def publish(self, event: EventMessage):
        if event.event_type in self.topic_subscribers:
            for callback in self.topic_subscribers[event.event_type]:
                asyncio.create_task(self._deliver(callback, event))

    async def _deliver(self, callback: Callable, event: EventMessage):
        try:
            callback(event)
        except Exception as e:
            print(f"Error delivering event {event.event_type}: {e}")
