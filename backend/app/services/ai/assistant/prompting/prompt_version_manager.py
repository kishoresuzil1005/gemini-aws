from typing import Dict, Any
from datetime import datetime

class PromptVersion:
    def __init__(self, version: str, description: str, system_prompt: str, is_active: bool = False):
        self.version = version
        self.description = description
        self.system_prompt = system_prompt
        self.is_active = is_active
        self.created_at = datetime.utcnow().isoformat()

class PromptVersionManager:
    """
    Manages versioned system prompts for A/B testing and safe rollouts.
    Allows switching between prompt strategies without redeploying.
    """
    def __init__(self):
        self._versions: Dict[str, PromptVersion] = {}
        self._active_version: str = "v1"

        # Seed with the default v1 system prompt
        self.register_version(PromptVersion(
            version="v1",
            description="Standard cloud operations assistant.",
            system_prompt="You are the AI Cloud Operating System. Help users manage and optimize their cloud intelligently.",
            is_active=True
        ))
        self.register_version(PromptVersion(
            version="v2",
            description="Enhanced reasoning with explicit step-by-step thinking.",
            system_prompt="You are the AI Cloud Operating System. Think step-by-step. Show your reasoning before conclusions. Cite all sources explicitly."
        ))

    def register_version(self, version: PromptVersion):
        self._versions[version.version] = version

    def set_active(self, version_id: str):
        if version_id not in self._versions:
            raise ValueError(f"Version '{version_id}' not found.")
        self._active_version = version_id
        print(f"[PromptVersionManager] Active prompt set to '{version_id}'")

    def get_active_prompt(self) -> str:
        return self._versions[self._active_version].system_prompt

    def list_versions(self) -> Dict[str, Any]:
        return {vid: {"description": v.description, "active": vid == self._active_version}
                for vid, v in self._versions.items()