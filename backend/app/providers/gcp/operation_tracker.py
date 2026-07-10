import time
from typing import Any

class OperationTracker:
    """Tracks asynchronous GCP operations until completion."""
    
    @staticmethod
    def wait_for_operation(client: Any, operation: Any, project: str, zone: str = None, region: str = None, timeout: int = 300) -> Any:
        """
        Waits for a GCP operation to complete.
        Supports zonal, regional, or global operations.
        """
        if not hasattr(operation, "status"):
            # It might not be an operation object, return as is
            return operation
            
        # In modern google-cloud-compute SDKs, operations might have a .result() method
        if hasattr(operation, "result"):
            return operation.result(timeout=timeout)
            
        return operation
