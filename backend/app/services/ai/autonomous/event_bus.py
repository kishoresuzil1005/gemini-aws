"""Event Bus — Phase 6"""
from __future__ import annotations
import asyncio, logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """Simple in-process async event bus. Replace with Kafka/SQS for production."""

    _handlers: Dict[str, List[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable) -> None:
        cls._handlers.setdefault(event_type, []).append(handler)
        logger.info("[EventBus] Subscribed %s → %s", event_type, handler.__name__)

    @classmethod
    async def publish(cls, event_type: str, payload: Dict[str, Any]) -> None:
        for handler in cls._handlers.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception as e:
                logger.error("[EventBus] Handler error for %s: %s", event_type, e)
