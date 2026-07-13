import time
import requests
from app.services.ai.assistant.llm.config import settings

class HealthManager:
    _last_check_time = 0
    _last_status = {"status": "unavailable", "ollama": False, "model": None, "response_time_ms": 0}

    @classmethod
    def get_health_status(cls, session: requests.Session) -> dict:
        current_time = time.time()
        
        # Return cached status if within TTL
        if current_time - cls._last_check_time < settings.health_cache_seconds:
            return cls._last_status

        start_time = time.time()
        try:
            # 1. Check Ollama API version
            r_version = session.get(f"{settings.ollama_url}/api/version", timeout=settings.timeout)
            r_version.raise_for_status()

            # 2. Check if the configured model is pulled
            r_tags = session.get(f"{settings.ollama_url}/api/tags", timeout=settings.timeout)
            r_tags.raise_for_status()
            
            models = [m.get("name") for m in r_tags.json().get("models", [])]
            has_model = settings.ollama_model in models
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if has_model:
                cls._last_status = {
                    "status": "healthy",
                    "ollama": True,
                    "model": settings.ollama_model,
                    "response_time_ms": response_time_ms
                }
            else:
                cls._last_status = {
                    "status": "model_missing",
                    "ollama": True,
                    "model": settings.ollama_model,
                    "response_time_ms": response_time_ms
                }

        except Exception as e:
            print("OLLAMA HEALTH CHECK ERROR:", e)
            cls._last_status = {
                "status": "unavailable",
                "ollama": False,
                "model": settings.ollama_model,
                "response_time_ms": int((time.time() - start_time) * 1000)
            }
            
        cls._last_check_time = current_time
        return cls._last_status

    @classmethod
    def check_health(cls, session: requests.Session) -> bool:
        status = cls.get_health_status(session)
        return status.get("status") == "healthy"