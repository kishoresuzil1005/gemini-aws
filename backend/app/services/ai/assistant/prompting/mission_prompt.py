from typing import Dict, Any, List

class MissionPromptBuilder:
    """
    Builds mission-aware system prompts, injecting current Mission state, 
    Objectives, and Progress into the Ollama context window.
    """
    def build_mission_context_block(self, mission: Dict[str, Any]) -> str:
        if not mission:
            return ""
        objectives = "\n".join(
            f"  - [{obj.get('status','PENDING')}] {obj.get('description','')}"
            for obj in mission.get("objectives", [])
        )
        return f"""
=== ACTIVE MISSION ===
Mission ID: {mission.get('mission_id')}
Title: {mission.get('title')}
Status: {mission.get('status')}
Progress: {mission.get('progress_pct', 0):.1f}%

Objectives:
{objectives}
=====================
"""

class WorkflowPromptBuilder:
    """
    Injects active workflow states and recent execution logs into the prompt.
    """
    def build_workflow_context_block(self, workflows: List[Dict[str, Any]]) -> str:
        if not workflows:
            return ""
        lines = [f"  [{w.get('status')}] {w.get('name')}" for w in workflows]
        return f"""
=== ACTIVE WORKFLOWS ===
{chr(10).join(lines)}
========================
"""

class KnowledgePromptBuilder:
    """
    Injects the most relevant Knowledge Graph nodes as grounded context.
    """
    def build_knowledge_block(self, resources: List[Dict[str, Any]]) -> str:
        if not resources:
            return ""
        lines = [f"  - {r.get('resource_id')} ({r.get('type')}) [{r.get('criticality', 'UNKNOWN')}]" for r in resources]
        return f"""
=== CLOUD KNOWLEDGE CONTEXT ===
{chr(10).join(lines)}
================================
""