import requests
import os


class OllamaService:

    def __init__(self):
        self.url = os.getenv(
            "OLLAMA_URL",
            "http://ollama:11434"
        )

        self.model = "qwen2.5:1.5b"
        self.session = requests.Session()

    def generate(self, prompt):

        response = self.session.post(
            f"{self.url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]
