import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.dependency_engine.engine import DependencyIntelligenceEngine

def test_engine():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        engine = DependencyIntelligenceEngine(bm.client)
        
        # We need a mock resource id to test it.
        # Let's say we have 'aws-prod-123' or similar. We will just pass a dummy string
        # since it's disconnected, it might return None. We just check no exception is raised.
        dummy_id = "test_resource_1"
        try:
            print("Testing get_dependencies...")
            engine.get_dependencies(dummy_id)
            print("Testing get_shortest_path...")
            engine.get_shortest_path(dummy_id, "test_resource_2")
            print("Testing analyze_root_cause...")
            engine.analyze_root_cause(dummy_id, "High CPU")
            print("Testing analyze_blast_radius...")
            engine.analyze_blast_radius(dummy_id)
            print("Testing analyze_critical_path...")
            engine.analyze_critical_path(dummy_id, "test_resource_2")
            print("Testing analyze_impact...")
            engine.analyze_impact(dummy_id, "Delete")
            print("Testing generate_recommendations...")
            engine.generate_recommendations(dummy_id)
            print("Testing AI Explanation...")
            engine.generate_ai_explanation(None)
            print("All Dependency Engine methods invoked successfully without AWS knowledge!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
            
if __name__ == "__main__":
    assert test_engine()
