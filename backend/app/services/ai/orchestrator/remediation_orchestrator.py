from typing import List
from app.services.ai.remediation_planner import RemediationPlanner
from app.services.ai.orchestrator.orchestration_models import ExecutionPackage
from app.services.ai.orchestrator.execution_planner import ExecutionPlanner
from app.services.ai.orchestrator.dependency_scheduler import DependencyScheduler
from app.services.ai.orchestrator.approval_engine import ApprovalEngine
from app.services.ai.orchestrator.rollback_planner import RollbackPlanner
from app.services.ai.orchestrator.validation_engine import ValidationEngine

class RemediationOrchestrator:
    def __init__(self):
        self.remediation_planner = RemediationPlanner()
        self.execution_planner = ExecutionPlanner()
        self.dependency_scheduler = DependencyScheduler()
        self.approval_engine = ApprovalEngine()
        self.rollback_planner = RollbackPlanner()
        self.validation_engine = ValidationEngine()

    def build_package(self, resource_id: str) -> List[ExecutionPackage]:
        # 1. Get raw remediation plans
        plans = self.remediation_planner.plan_for_resource(resource_id)
        
        packages = []
        for plan in plans:
            # Extract resource type from Neo4j (via DependencyScheduler)
            resource_type = "Resource"
            if self.dependency_scheduler.neo4j.driver:
                try:
                    res = self.dependency_scheduler.neo4j.query("MATCH (n {id:$id}) RETURN labels(n)[0] as type", id=resource_id)
                    if res and res[0].get("type"):
                        resource_type = res[0]["type"]
                except Exception:
                    pass

            # 2. Plan Execution Steps
            raw_steps = self.execution_planner.plan(plan)
            
            # 3. Schedule with Dependencies
            ordered_steps = self.dependency_scheduler.schedule(resource_id, raw_steps)
            
            # 4. Determine Approvals
            approval = self.approval_engine.determine_approval(resource_type, plan.priority)
            
            # 5. Generate Rollback Plan
            rollback = self.rollback_planner.generate_rollback(ordered_steps)
            
            # 6. Generate Validation Plan
            validation = self.validation_engine.generate_validation(resource_type, resource_id)
            
            packages.append(ExecutionPackage(
                resource_id=resource_id,
                issue=plan.issue,
                risk_level=plan.priority,
                approval=approval,
                execution_plan=ordered_steps,
                rollback=rollback,
                validation=validation
            ))
            
        return packages

    def build_environment_packages(self) -> List[ExecutionPackage]:
        # Get raw remediation plans for the environment
        plans = self.remediation_planner.plan_environment()
        
        packages = []
        for plan in plans:
            # We must determine resource type
            resource_type = "Resource"
            if self.dependency_scheduler.neo4j.driver:
                try:
                    res = self.dependency_scheduler.neo4j.query("MATCH (n {id:$id}) RETURN labels(n)[0] as type", id=plan.resource_id)
                    if res and res[0].get("type"):
                        resource_type = res[0]["type"]
                except Exception:
                    pass
                    
            raw_steps = self.execution_planner.plan(plan)
            ordered_steps = self.dependency_scheduler.schedule(plan.resource_id, raw_steps)
            approval = self.approval_engine.determine_approval(resource_type, plan.priority)
            rollback = self.rollback_planner.generate_rollback(ordered_steps)
            validation = self.validation_engine.generate_validation(resource_type, plan.resource_id)
            
            packages.append(ExecutionPackage(
                resource_id=plan.resource_id,
                issue=plan.issue,
                risk_level=plan.priority,
                approval=approval,
                execution_plan=ordered_steps,
                rollback=rollback,
                validation=validation
            ))
            
        return packages
