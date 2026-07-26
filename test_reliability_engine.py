import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine
from app.services.performance_engine.engine import PerformanceIntelligenceEngine
from app.services.reliability_engine.engine import ReliabilityIntelligenceEngine

def test_engine():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        dep_engine = DependencyIntelligenceEngine(bm.client)
        sec_engine = SecurityIntelligenceEngine(bm.client, dep_engine)
        cost_engine = CostIntelligenceEngine(bm.client, dep_engine, sec_engine)
        perf_engine = PerformanceIntelligenceEngine(bm.client, dep_engine, sec_engine, cost_engine)
        rel_engine = ReliabilityIntelligenceEngine(bm.client, dep_engine, sec_engine, cost_engine, perf_engine)
        
        dummy_id = "test_resource_1"
        try:
            print("Testing build_reliability_profile...")
            profile = rel_engine.build_reliability_profile(dummy_id)
            print("Testing AI Explanation...")
            rel_engine.generate_ai_explanation(profile)
            
            print("All Reliability Engine methods invoked successfully without AWS Knowledge!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
            
if __name__ == "__main__":
    assert test_engine()
