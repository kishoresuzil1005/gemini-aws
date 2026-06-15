import requests

OLLAMA_URL = "http://ollama:11434/api/generate"

class OllamaService:

    @staticmethod
    def generate(prompt: str):

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["response"]
