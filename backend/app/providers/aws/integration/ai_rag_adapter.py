from typing import Dict, Any
from ..discovery.aws_discovery import AWSDiscoveryEngine

class AIRAGAdapter:
    """
    Connects the Phase 15 AI Intelligence Layer directly to the AWS Discovery Engine.
    When a user asks "Which EC2 instances are exposed?", this adapter provides live context.
    """
    def __init__(self, discovery_engine: AWSDiscoveryEngine):
        self.discovery = discovery_engine

    def get_live_context(self) -> str:
        print("[AIRAGAdapter] Fetching live AWS context for AI RAG pipeline...")
        inventory = self.discovery.resource_discovery.discover_all()
        # Summarize for the LLM Context Window
        return f"Currently running {len(inventory.get('ec2_instances', []))} EC2 instances."
