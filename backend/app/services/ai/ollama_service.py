import os
import requests
import logging

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, host: str = None, model: str = None):
        self.host = host or os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")

    def generate(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"

        logger.debug(f"OLLAMA URL: {url}")
        logger.debug(f"OLLAMA MODEL: {self.model}")
        logger.info(f"Generating response from Ollama (Prompt length: {len(prompt)})")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.Timeout:
            logger.exception("Ollama request timed out after 120 seconds.")
            return "Error communicating with Ollama: TimeoutException"
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network error communicating with Ollama: {e}")
            return f"Error communicating with Ollama: {str(e)}"
        except ValueError as e:
            logger.exception(f"Failed to parse JSON response from Ollama: {e}")
            return f"Error parsing Ollama response: {str(e)}"
