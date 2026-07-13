import time
import logging

logger = logging.getLogger(__name__)

class GraphLockManager:
    """
    Distributed lock to prevent parallel discoveries from corrupting graph state.
    Typically backed by Redis or similar distributed cache.
    """
    def __init__(self):
        self._locks = {}

    def acquire_lock(self, lock_key: str, timeout: int = 60) -> bool:
        if self._locks.get(lock_key):
            logger.warning(f"Lock {lock_key} is already acquired.")
            return False
        self._locks[lock_key] = True
        logger.info(f"Acquired graph lock: {lock_key}")
        return True

    def release_lock(self, lock_key: str):
        if lock_key in self._locks:
            del self._locks[lock_key]
            logger.info(f"Released graph lock: {lock_key}")