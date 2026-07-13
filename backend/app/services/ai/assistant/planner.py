import uuid
from typing import List, Optional
from app.services.ai.assistant.execution_plan import (
    ExecutionPlan, 
    ExecutionStep, 
    ToolRequirement, 
    ExecutionContext,
    PlanStatus
)

from app.services.ai.assistant.planner_rules import PlannerRules

class Planner:
    def create_plan(
        self, 
        conversation_id: str, 
        intent: str, 
        resource_id: Optional[str] = None, 
        resource_type: Optional[str] = None
    ) -> ExecutionPlan:
        """
        Creates a high-level execution plan based on the user intent and resource.
        It answers one question: 'What should we do?'
        """
        objective = self._determine_objective(intent)
        tools = self._select_tools(intent)
        steps = self._build_execution_steps(tools)
        expected_outputs = self._determine_expected_outputs(tools)
        
        context = ExecutionContext(
            conversation_id=conversation_id,
            request_id=str(uuid.uuid4()),
            intent=intent,
            resource_id=resource_id,
            resource_type=resource_type
        )
        
        plan = ExecutionPlan(
            plan_id=str(uuid.uuid4()),
            objective=objective,
            context=context,
            status=PlanStatus.PENDING,
            required_tools=[ToolRequirement(tool_name=t) for t in tools],
            steps=steps,
            expected_outputs=expected_outputs,
            estimated_steps=len(steps)
        )
        
        self._validate_plan(plan)
        return plan

    def _determine_objective(self, intent: str) -> str:
        return PlannerRules.get_objective(intent)

    def _select_tools(self, intent: str) -> List[str]:
        return PlannerRules.get_tools(intent)

    def _build_execution_steps(self, tools: List[str]) -> List[ExecutionStep]:
        # Always run GRAPH first if present, then others, then RECOMMENDATION last
        ordered_tools = []
        
        if "GRAPH" in tools:
            ordered_tools.append("GRAPH")
            
        for tool in tools:
            if tool not in ["GRAPH", "RECOMMENDATION"]:
                ordered_tools.append(tool)
                
        if "RECOMMENDATION" in tools:
            ordered_tools.append("RECOMMENDATION")
            
        steps = []
        for i, tool_name in enumerate(ordered_tools):
            depends_on = []
            if i > 0:
                # the current step depends on the immediately preceding step
                depends_on = [ordered_tools[i - 1]]
                
            steps.append(ExecutionStep(
                step_number=i + 1,
                tool_name=tool_name,
                purpose=f"Execute {tool_name} analysis",
                depends_on=depends_on,
                expected_outputs=[f"{tool_name} results"]
            ))
            
        return steps

    def _determine_expected_outputs(self, tools: List[str]) -> List[str]:
        outputs = []
        if "GRAPH" in tools:
            outputs.append("Dependencies and Topology")
        if "SECURITY" in tools:
            outputs.append("Security Findings")
        if "RECOMMENDATION" in tools:
            outputs.append("Actionable Recommendations")
        if "COST" in tools:
            outputs.append("Cost Metrics")
        if "INVENTORY" in tools:
            outputs.append("Resource Details")
        return outputs

    def _validate_plan(self, plan: ExecutionPlan) -> None:
        if not plan.required_tools:
            plan.status = PlanStatus.FAILED
            plan.context.metadata["error"] = "No tools selected for execution."
            return
            
        # Check for duplicate tools
        tool_names = [t.tool_name for t in plan.required_tools]
        if len(tool_names) != len(set(tool_names)):
            plan.status = PlanStatus.FAILED
            plan.context.metadata["error"] = "Duplicate tools found in plan."
            return
            
        # Verify valid dependencies
        step_names = {step.tool_name for step in plan.steps}
        for step in plan.steps:
            for dependency in step.depends_on:
                if dependency not in step_names:
                    plan.status = PlanStatus.FAILED
                    plan.context.metadata["error"] = f"Invalid dependency '{dependency}' for tool '{step.tool_name}'."
                    retur