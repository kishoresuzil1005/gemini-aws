import time
from datetime import datetime, timezone
from typing import List
from app.services.ai.assistant.execution_plan import ExecutionPlan, ToolResult, PlanStatus, ToolStatus
from app.services.ai.assistant.tool_router import ToolRouter

class PlanExecutor:
    def __init__(self, router: ToolRouter):
        self.router = router

    def execute(self, plan: ExecutionPlan, **kwargs) -> List[ToolResult]:
        """
        Executes the provided execution plan sequentially, respecting dependencies and retries.
        Answers one question: 'How do we execute the plan?'
        """
        if plan.status == PlanStatus.FAILED:
            return []
            
        plan.status = PlanStatus.RUNNING
        results: List[ToolResult] = []
        successful_tools = set()
        
        # Build lookup for tool requirements to fetch retry counts and timeouts
        req_map = {req.tool_name: req for req in plan.required_tools}
        
        for step in plan.steps:
            tool_name = step.tool_name
            started_at = datetime.now(timezone.utc)
            start_time = time.time()
            
            # 1. Dependency Check
            failed_deps = [dep for dep in step.depends_on if dep not in successful_tools]
            if failed_deps:
                results.append(ToolResult(
                    tool_name=tool_name,
                    status=ToolStatus.SKIPPED,
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                    execution_time_ms=0,
                    warnings=[f"Skipped because upstream dependencies failed: {', '.join(failed_deps)}"]
                ))
                continue
            
            # 2. Tool Resolution
            tool = self.router.get_tool(tool_name)
            if not tool:
                results.append(ToolResult(
                    tool_name=tool_name,
                    status=ToolStatus.FAILED,
                    started_at=started_at,
                    finished_at=datetime.now(timezone.utc),
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    errors=[f"Tool '{tool_name}' is not registered in ToolRegistry."],
                ))
                continue
                
            # 3. Execution with Retries
            req = req_map.get(tool_name)
            max_retries = req.retry_count if req else 0
            
            attempt = 0
            final_status = ToolStatus.FAILED
            response = None
            last_error = None
            
            while attempt <= max_retries:
                attempt += 1
                try:
                    response = tool.execute(resource_id=plan.context.resource_id, **kwargs)
                    raw_status = getattr(response, "status", "ERROR").upper()
                    if raw_status == "SUCCESS":
                        final_status = ToolStatus.SUCCESS
                        successful_tools.add(tool_name)
                        break
                    else:
                        last_error = response.metadata.get("error") if hasattr(response, "metadata") else "Tool returned non-success status."
                except Exception as e:
                    last_error = str(e)
                    
            finished_at = datetime.now(timezone.utc)
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # 4. Standardize ToolResult
            if final_status == ToolStatus.SUCCESS:
                results.append(ToolResult(
                    tool_name=tool_name,
                    status=final_status,
                    started_at=started_at,
                    finished_at=finished_at,
                    execution_time_ms=execution_time_ms,
                    context=response.context if hasattr(response, "context") else {},
                    metadata=response.metadata if hasattr(response, "metadata") else {}
                ))
            else:
                results.append(ToolResult(
                    tool_name=tool_name,
                    status=ToolStatus.FAILED,
                    started_at=started_at,
                    finished_at=finished_at,
                    execution_time_ms=execution_time_ms,
                    errors=[last_error] if last_error else ["Tool execution failed"]
                ))
                
        # 5. Determine Final Plan Status
        failed_count = sum(1 for r in results if r.status == ToolStatus.FAILED)
        skipped_count = sum(1 for r in results if r.status == ToolStatus.SKIPPED)
        
        if failed_count == 0 and skipped_count == 0:
            plan.status = PlanStatus.COMPLETED
        elif failed_count + skipped_count == len(results):
            plan.status = PlanStatus.FAILED
        else:
            plan.status = PlanStatus.PARTIAL_SUCCESS
            
        return results
