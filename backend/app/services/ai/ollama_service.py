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

        print("=" * 60)
        print("OLLAMA URL :", url)
        print("OLLAMA MODEL :", self.model)
        print("PROMPT LENGTH :", len(prompt))

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"Failed to generate response from Ollama: {e}")
            return f"Error communicating with Ollama: {str(e)}"
