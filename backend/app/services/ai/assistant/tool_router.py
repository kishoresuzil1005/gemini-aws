from typing import Dict, Any
from app.services.ai.assistant.assistant_models import ToolResponse
from app.services.ai.assistant.tool_registry import ToolRegistry
from app.services.ai.assistant.tools.security_tool import SecurityTool
from app.services.ai.assistant.tools.dependency_tool import DependencyTool
from app.services.ai.assistant.tools.blast_radius_tool import BlastRadiusTool
from app.services.ai.assistant.tools.root_cause_tool import RootCauseTool
from app.services.ai.assistant.tools.recommendation_tool import RecommendationTool
from app.services.ai.assistant.tools.remediation_tool import RemediationTool
from app.services.ai.assistant.tools.orchestration_tool import OrchestrationTool
from app.services.ai.assistant.tools.inventory_tool import InventoryTool
from app.services.ai.assistant.tools.documentation_tool import DocumentationTool

class ToolRouter:
    def __init__(self):
        self.registry = ToolRegistry()
        self.registry.register(SecurityTool())
        self.registry.register(DependencyTool())
        self.registry.register(BlastRadiusTool())
        self.registry.register(RootCauseTool())
        self.registry.register(RecommendationTool())
        self.registry.register(RemediationTool())
        self.registry.register(OrchestrationTool())
        self.registry.register(InventoryTool())
        self.registry.register(DocumentationTool())

    def route(self, intent: str, resource_id: str, **kwargs) -> ToolResponse:
        """
        Routes the classified intent to the appropriate registered tool.
        """
        tool = self.registry.get_tool(intent)
        if not tool:
            # Fallback to recommendation or documentation if tool not found
            if not resource_id:
                tool = self.registry.get_tool("DOCUMENTATION")
            else:
                tool = self.registry.get_tool("RECOMMENDATION")
                
        if tool:
            return tool.execute(resource_id=resource_id, **kwargs)
            
        return ToolResponse(
            tool_name="UNKNOWN",
            status="ERROR",
            context={"error": f"No tool registered for intent {intent}"}
        )
