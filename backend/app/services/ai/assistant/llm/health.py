import time
import requests
from app.services.ai.assistant.llm.config import settings

class HealthManager:
    _last_check_time = 0
    _last_status = False

    @classmethod
    def check_health(cls, session: requests.Session) -> bool:
        current_time = time.time()
        
        # Return cached status if within TTL
        if current_time - cls._last_check_time < settings.health_cache_seconds:
            return cls._last_status

        # Perform the actual check
        try:
            r = session.get(f"{settings.ollama_url}/api/version", timeout=settings.timeout)
            cls._last_status = (r.status_code == 200)
        except Exception as e:
            print("OLLAMA HEALTH CHECK ERROR:", e)
            cls._last_status = False
            
        cls._last_check_time = current_time
        return cls._last_status
