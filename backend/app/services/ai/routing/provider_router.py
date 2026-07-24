from enum import Enum
from app.services.ai.assistant.llm.base_provider import BaseProvider

class ProviderType(str, Enum):
    OLLAMA = "OLLAMA"
    OPENAI = "OPENAI"
    BEDROCK = "BEDROCK"
    GEMINI = "GEMINI"

class ProviderRouter:
    @staticmethod
    def get_provider(provider_type: ProviderType, default_provider: BaseProvider) -> BaseProvider:
        if provider_type == ProviderType.OLLAMA:
            return default_provider
        raise NotImplementedError(f"Provider {provider_type} is not yet implemented.")
