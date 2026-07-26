import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine

def test_engine():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        dep_engine = DependencyIntelligenceEngine(bm.client)
        sec_engine = SecurityIntelligenceEngine(bm.client, dep_engine)
        cost_engine = CostIntelligenceEngine(bm.client, dep_engine, sec_engine)
        
        dummy_id = "test_resource_1"
        try:
            print("Testing analyze_resource_cost...")
            cost_engine.analyze_resource_cost(dummy_id)
            print("Testing analyze_cost_attribution...")
            cost_engine.analyze_cost_attribution(dummy_id)
            print("Testing detect_idle_resources...")
            cost_engine.detect_idle_resources(dummy_id)
            print("Testing generate_optimizations...")
            cost_engine.generate_optimizations(dummy_id)
            print("Testing analyze_anomaly...")
            cost_engine.analyze_anomaly(dummy_id)
            
            b_cost = cost_engine.generate_business_cost(dummy_id)
            print("Testing AI Explanation...")
            cost_engine.generate_ai_explanation(b_cost, [])
            
            print("All Cost Engine methods invoked successfully without AWS knowledge!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
            
if __name__ == "__main__":
    assert test_engine()
