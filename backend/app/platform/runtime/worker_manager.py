import asyncio
from typing import Dict, Any, Callable

class TaskQueue:
    """
    Distributed Task Queue using Celery/Redis in production.
    Mocked here using asyncio queues for the skeleton.
    """
    def __init__(self):
        self.queue = asyncio.Queue()

    async def enqueue(self, task_name: str, payload: Dict[str, Any]):
        print(f"[TaskQueue] Enqueued task: {task_name}")
        await self.queue.put({"name": task_name, "payload": payload})

class WorkerManager:
    """
    Background workers that process long-running missions and workflows asynchronously.
    """
    def __init__(self, queue: TaskQueue, handlers: Dict[str, Callable]):
        self.queue = queue
        self.handlers = handlers
        self.is_running = False

    async def start_workers(self, worker_count: int = 4):
        self.is_running = True
        workers = [asyncio.create_task(self._worker_loop(i)) for i in range(worker_count)]
        print(f"[WorkerManager] Started {worker_count} background workers.")
        await asyncio.gather(*workers)

    async def _worker_loop(self, worker_id: int):
        while self.is_running:
            task = await self.queue.queue.get()
            name = task["name"]
            if name in self.handlers:
                print(f"[Worker {worker_id}] Executing {name}...")
                try:
                    await self.handlers[name](task["payload"])
                except Exception as e:
                    print(f"[Worker {worker_id}] Error in task {name}: {e}")
            self.queue.queue.task_done()
