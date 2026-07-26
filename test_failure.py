import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
import traceback

def test_failure_recovery():
    print("Testing Failure Recovery...")
    bm = BootstrapManager.get_instance()
    
    # Simulate a failure in get_default_client
    try:
        from unittest.mock import patch
        with patch('app.bootstrap.get_default_client', side_effect=Exception("Simulated Graph Failure")):
            bm.initialize_platform()
    except Exception as e:
        print(f"Caught exception: {e}")
        
    print(f"Health Status: {bm.get_health()}")
    print(f"Readiness: {bm.get_readiness()}")
    
    # Attempt shutdown after failure
    try:
        bm.shutdown_platform()
        print("Shutdown after failure succeeded.")
    except Exception as e:
        print(f"Shutdown after failure error: {e}")

if __name__ == "__main__":
    test_failure_recovery()
