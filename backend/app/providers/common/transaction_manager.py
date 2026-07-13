from typing import List, Dict, Any, Callable
import logging

logger = logging.getLogger(__name__)

class ProviderTransactionManager:
    """
    Manages atomic operations across providers.
    Allows for commit and rollback to prevent half-modified infrastructure states.
    """
    def __init__(self):
        self._operations: List[Dict[str, Any]] = []

    def add_operation(self, execute_fn: Callable, rollback_fn: Callable, description: str):
        self._operations.append({
            "execute": execute_fn,
            "rollback": rollback_fn,
            "description": description,
            "status": "pending"
        })

    def commit(self) -> bool:
        executed_ops = []
        for op in self._operations:
            logger.info(f"Executing: {op['description']}")
            try:
                op['execute']()
                op['status'] = "success"
                executed_ops.append(op)
            except Exception as e:
                logger.error(f"Transaction failed at step: {op['description']}. Error: {e}")
                self._rollback(executed_ops)
                return False
        
        self._operations.clear()
        return True

    def _rollback(self, executed_ops: List[Dict[str, Any]]):
        logger.warning("Initiating rollback for failed transaction...")
        for op in reversed(executed_ops):
            logger.info(f"Rolling back: {op['description']}")
            try:
                op['rollback']()
            except Exception as e:
                logger.critical(f"Rollback failed for {op['description']}. Manual intervention required! Error: {e}")
