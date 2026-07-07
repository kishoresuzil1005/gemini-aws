from pydantic_settings import BaseSettings

class AISettings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    timeout: int = 15
    max_retries: int = 3
    health_cache_seconds: int = 60
    stream_enabled: bool = False

    class Config:
        env_prefix = "AI_"

settings = AISettings()
