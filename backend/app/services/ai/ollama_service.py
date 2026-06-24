import requests
import os

class OllamaService:

    def __init__(self):
        self.url = os.getenv(
            "OLLAMA_URL",
            "http://ollama:11434"
        )
        self.model = "qwen2.5:3b"

    def generate(self, prompt: str):
        response = requests.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        data = response.json()
        return data.get(
            "response",
            ""
        )
