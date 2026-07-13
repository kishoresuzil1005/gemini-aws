import os

class AISettings:
    def __init__(self):
        self.ollama_url: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
        self.timeout: int = int(os.getenv("AI_TIMEOUT", "120"))
        self.max_retries: int = int(os.getenv("AI_MAX_RETRIES", "3"))
        self.health_cache_seconds: int = int(os.getenv("AI_HEALTH_CACHE_SECONDS", "60"))
        self.stream_enabled: bool = os.getenv("AI_STREAM_ENABLED", "false").lower() == "true"

settings = AISettings(