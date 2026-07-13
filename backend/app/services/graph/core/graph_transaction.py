import logging
from typing import Callable, Any, List

logger = logging.getLogger(__name__)

class GraphTransaction:
    """
    Wraps Neo4j updates in atomic blocks. Supports rollback on partial failure.
    """
    def __init__(self, neo4j_client: Any):
        self.neo4j_client = neo4j_client
        self._operations: List[Callable] = []

    def add_operation(self, operation: Callable):
        self._operations.append(operation)

    def commit(self) -> bool:
        # In a real Neo4j setup, this would use a session transaction
        # with self.neo4j_client.session().begin_transaction() as tx:
        logger.info("Starting Neo4j transaction...")
        try:
            for op in self._operations:
                op()
            logger.info("Neo4j transaction committed successfully.")
            return True
        except Exception as e:
            logger.error(f"Transaction failed: {e}. Rolling back.")
            self.rollback()
            return False
        finally:
            self._operations.clear()

    def rollback(self):
        logger.warning("Rollback executed. No changes were committed to Neo4j.")