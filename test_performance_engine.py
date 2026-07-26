import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.dependency_engine.engine import DependencyIntelligenceEngine
from app.services.security_engine.engine import SecurityIntelligenceEngine
from app.services.cost_engine.engine import CostIntelligenceEngine
from app.services.performance_engine.engine import PerformanceIntelligenceEngine

def test_engine():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        dep_engine = DependencyIntelligenceEngine(bm.client)
        sec_engine = SecurityIntelligenceEngine(bm.client, dep_engine)
        cost_engine = CostIntelligenceEngine(bm.client, dep_engine, sec_engine)
        perf_engine = PerformanceIntelligenceEngine(bm.client, dep_engine, sec_engine, cost_engine)
        
        dummy_id = "test_resource_1"
        try:
            print("Testing analyze_latency...")
            perf_engine.analyze_latency(dummy_id)
            print("Testing analyze_throughput...")
            perf_engine.analyze_throughput(dummy_id)
            print("Testing analyze_utilization...")
            perf_engine.analyze_utilization(dummy_id)
            print("Testing analyze_bottlenecks...")
            perf_engine.analyze_bottlenecks(dummy_id)
            print("Testing predictive and trade-off...")
            perf_engine.generate_predictive_report(dummy_id)
            perf_engine.analyze_trade_offs(dummy_id)
            print("Testing risk and cross-engine...")
            perf_engine.calculate_performance_risk(dummy_id)
            perf_engine.analyze_cross_engine(dummy_id)
            print("Testing build_performance_profile...")
            profile = perf_engine.build_performance_profile(dummy_id)
            print("Testing AI Explanation...")
            perf_engine.generate_ai_explanation(profile)
            
            print("All Performance Engine methods invoked successfully without CloudWatch knowledge!")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
            
if __name__ == "__main__":
    assert test_engine()
