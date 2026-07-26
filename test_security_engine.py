import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.security_engine.models import SecurityPosture

def test_engine():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        dep_engine = DependencyIntelligenceEngine(bm.client)
        sec_engine = SecurityIntelligenceEngine(bm.client, dep_engine)
        
        dummy_id = "test_resource_1"
        try:
            print("Testing analyze_attack_paths...")
            sec_engine.analyze_attack_paths(dummy_id)
            print("Testing analyze_exposure...")
            sec_engine.analyze_exposure(dummy_id)
            print("Testing analyze_iam...")
            sec_engine.analyze_iam(dummy_id)
            print("Testing analyze_network...")
            sec_engine.analyze_network(dummy_id)
            print("Testing analyze_data_security...")
            sec_engine.analyze_data_security(dummy_id)
            
            posture = SecurityPosture(overall_score=80, issues=[], attack_paths=[])
            print("Testing AI Explanation...")
            sec_engine.generate_ai_explanation(posture)
            
            print("All Security Engine methods invoked successfully without AWS knowledge!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
            
if __name__ == "__main__":
    assert test_engine()
