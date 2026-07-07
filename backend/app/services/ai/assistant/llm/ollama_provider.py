import time
import json
from typing import List, Dict, Union, AsyncGenerator
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.config import AISettings
from app.services.ai.assistant.llm.connection_pool import ConnectionPool
from app.services.ai.assistant.llm.health import HealthManager
from app.services.ai.assistant.llm.retry import with_retry
from app.services.ai.assistant.llm.exceptions import LlmConnectionError, LlmTimeoutError, LlmProviderError
from app.services.ai.assistant.llm.metrics import MetricsTracker

class OllamaProvider(BaseProvider):
    def __init__(self, settings: AISettings):
        super().__init__(settings)
        self.session = ConnectionPool.get_session()

    def health_check(self) -> bool:
        return HealthManager.check_health(self.session)

    @with_retry(max_retries=3, base_delay=1.0)
    def _execute_request(self, url: str, payload: dict, stream: bool):
        try:
            response = self.session.post(url, json=payload, timeout=self.settings.timeout, stream=stream)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            raise LlmTimeoutError("Request to Ollama timed out")
        except requests.exceptions.ConnectionError:
            raise LlmConnectionError("Failed to connect to Ollama")
        except Exception as e:
            raise LlmProviderError(f"Unexpected error communicating with Ollama: {str(e)}")

    def generate_response(self, messages: List[Dict[str, str]], request_id: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        start_time = time.time()
        
        if not self.health_check():
            MetricsTracker.record_failure(0)
            return "Error: Ollama is currently unavailable. Please check the AI engine."

        url = f"{self.settings.ollama_url}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": stream
        }

        try:
            import requests # Imported locally for exception catching inside retry loop
            if not stream:
                response = self._execute_request(url, payload, stream=False)
                data = response.json()
                result = data.get("message", {}).get("content", "")
                
                latency = int((time.time() - start_time) * 1000)
                MetricsTracker.record_success(latency)
                print(f"[Req: {request_id}] LLM Generation Success ({latency}ms)")
                return result
            else:
                # Basic stream handling via generator
                response = self._execute_request(url, payload, stream=True)
                
                async def stream_generator():
                    full_text = ""
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            if "message" in chunk and "content" in chunk["message"]:
                                content = chunk["message"]["content"]
                                full_text += content
                                yield content
                    
                    latency = int((time.time() - start_time) * 1000)
                    MetricsTracker.record_success(latency)
                    print(f"[Req: {request_id}] LLM Stream Generation Success ({latency}ms)")
                    
                return stream_generator()
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            MetricsTracker.record_failure(latency)
            print(f"[Req: {request_id}] LLM Generation Failed: {str(e)}")
            return f"Error communicating with Ollama: {str(e)}"
