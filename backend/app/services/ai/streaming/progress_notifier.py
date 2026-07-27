"""
SSE Progress Notifier — Phase 1 / Phase 12
============================================
Emits server-sent events for each pipeline stage so the frontend
can display a live progress checklist.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from asyncio import Queue
from enum import Enum
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)


class Stage(str, Enum):
    INTENT_CLASSIFIED    = "intent_classified"
    RESOURCE_RESOLVED    = "resource_resolved"
    GRAPH_BUILT          = "graph_built"
    PROVIDER_STARTED     = "provider_started"
    PROVIDER_DONE        = "provider_done"
    CONTEXT_AGGREGATED   = "context_aggregated"
    PROMPT_BUILT         = "prompt_built"
    LLM_STARTED          = "llm_started"
    LLM_STREAMING        = "llm_streaming"
    DONE                 = "done"
    ERROR                = "error"


class ProgressNotifier:
    """
    Collects pipeline progress events and streams them as SSE.

    Usage:
        notifier = ProgressNotifier()
        # In orchestrator:
        await notifier.emit(Stage.INTENT_CLASSIFIED, {"intent": "health_check"})
        # In FastAPI endpoint:
        return StreamingResponse(notifier.stream(), media_type="text/event-stream")
    """

    def __init__(self):
        self._queue: Queue = Queue()
        self._done = False

    async def emit(self, stage: Stage, data: Optional[dict] = None) -> None:
        event = {
            "stage": stage.value,
            "ts": round(time.time() * 1000),
            "data": data or {},
        }
        await self._queue.put(event)
        logger.debug("[SSE] %s %s", stage.value, data)

    async def close(self) -> None:
        self._done = True
        await self._queue.put(None)  # sentinel

    async def stream(self) -> AsyncIterator[str]:
        """Yields SSE-formatted strings for StreamingResponse."""
        while True:
            event = await self._queue.get()
            if event is None:
                yield "data: [DONE]\n\n"
                break
            yield f"data: {json.dumps(event)}\n\n"

    # Sync helper for non-async callers
    def emit_sync(self, stage: Stage, data: Optional[dict] = None) -> None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.emit(stage, data))
            else:
                loop.run_until_complete(self.emit(stage, data))
        except Exception:
            pass
