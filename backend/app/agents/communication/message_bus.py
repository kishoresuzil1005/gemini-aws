from typing import Dict, Callable, List
from ..base.base_message import AgentMessage
import asyncio

class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, agent_id: str, callback: Callable[[AgentMessage], None]):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    async def publish(self, message: AgentMessage):
        if message.receiver_id in self.subscribers:
            for callback in self.subscribers[message.receiver_id]:
                # In a real system, this might push to a queue (Kafka, RabbitMQ)
                asyncio.create_task(self._deliver(callback, message))

    async def _deliver(self, callback: Callable, message: AgentMessage):
        try:
            callback(message)
        except Exception as e:
            print(f"Error delivering message to {message.receiver_id}: {e}")
