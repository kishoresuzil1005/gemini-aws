import time
import json
import logging
import requests
from typing import List, Dict, Union, AsyncGenerator
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.llm.config import AISettings
from app.services.ai.assistant.llm.connection_pool import ConnectionPool
from app.services.ai.assistant.llm.health import HealthManager
from app.services.ai.assistant.llm.retry import with_retry
from app.services.ai.assistant.llm.exceptions import LlmConnectionError, LlmTimeoutError, LlmProviderError
from app.services.ai.assistant.llm.metrics import MetricsTracker

logger = logging.getLogger("OllamaProvider")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


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

    def _format_error(self, code: str, message: str) -> str:
        return json.dumps({
            "status": "error",
            "code": code,
            "message": message,
            "details": {
                "url": self.settings.ollama_url,
                "timeout": self.settings.timeout,
                "retry": self.settings.max_retries
            }
        })

    def generate_response(self, messages: List[Dict[str, str]], request_id: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        start_time = time.time()
        logger.info(f"[Req: {request_id}] Connecting to Ollama at {self.settings.ollama_url}")
        
        status = HealthManager.get_health_status(self.session)
        if status.get("status") != "healthy":
            latency = int((time.time() - start_time) * 1000)
            MetricsTracker.record_failure(latency)
            if status.get("status") == "model_missing":
                logger.error(f"[Req: {request_id}] Model {self.settings.ollama_model} is missing")
                return self._format_error("MODEL_NOT_FOUND", f"Model {self.settings.ollama_model} is not available on Ollama server.")
            else:
                logger.error(f"[Req: {request_id}] Ollama connection failed")
                return self._format_error("OLLAMA_CONNECTION_FAILED", "Cannot connect to Ollama server.")
                
        logger.info(f"[Req: {request_id}] Health OK. Model {self.settings.ollama_model} Loaded.")

        url = f"{self.settings.ollama_url}/api/chat"
        payload = {
            "model": self.settings.ollama_model,
            "messages": messages,
            "stream": stream
        }

        try:
            logger.info(f"[Req: {request_id}] Chat Started")
            if not stream:
                response = self._execute_request(url, payload, stream=False)
                data = response.json()
                result = data.get("message", {}).get("content", "")
                
                latency = int((time.time() - start_time) * 1000)
                MetricsTracker.record_success(latency)
                logger.info(f"[Req: {request_id}] Chat Finished. Elapsed {latency / 1000.0} sec")
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
                    logger.info(f"[Req: {request_id}] Chat Finished (Stream). Elapsed {latency / 1000.0} sec")
                    
                return stream_generator()
        except LlmTimeoutError as e:
            latency = int((time.time() - start_time) * 1000)
            MetricsTracker.record_failure(latency)
            logger.error(f"[Req: {request_id}] Timeout Error: {str(e)}")
            return self._format_error("LLM_TIMEOUT", "The AI model did not respond within the time limit.")
        except Exception as e:
            latency = int((time.time() - start_time) * 1000)
            MetricsTracker.record_failure(latency)
            logger.error(f"[Req: {request_id}] Generation Failed: {str(e)}")
            return self._format_error("OLLAMA_ERROR", f"Error communicating with Ollama: {str(e)}")
