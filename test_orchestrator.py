import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.bootstrap import BootstrapManager
from app.services.orchestrator.engine import EnterpriseIntelligenceOrchestrator

def test_orchestrator():
    bm = BootstrapManager.get_instance()
    bm.initialize_platform()
    
    if bm.client:
        orchestrator = EnterpriseIntelligenceOrchestrator(bm.client)
        
        scenarios = [
            ("ALB 502 Bad Gateway", "res:alb_1"),
            ("EC2 CPU Saturation", "res:ec2_2"),
            ("RDS Connection Exhaustion", "res:rds_3"),
            ("Lambda Timeout", "res:lambda_4"),
            ("S3 Public Bucket", "res:s3_5")
        ]
        
        for incident_name, resource_id in scenarios:
            print(f"Executing Scenario: {incident_name} on {resource_id}...")
            try:
                report = orchestrator.execute_scenario(incident_name, resource_id)
                ai_explanation = orchestrator.generate_ai_explanation(report)
                print(f"Success: {incident_name}")
                print(ai_explanation[:200] + "...\n")
            except Exception as e:
                print(f"Failed Scenario: {incident_name} - {str(e)}")
                return False
                
        print("All scenarios orchestrated and validated successfully across 5 engines!")
        return True

if __name__ == "__main__":
    assert test_orchestrator()
