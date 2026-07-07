import requests
import json
from typing import List, Dict, Union, AsyncGenerator
from app.services.ai.assistant.llm_provider import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        import os
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print("OLLAMA ERROR:", e)
            return False

    def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        if not self.health_check():
            return "Error: Ollama is currently unavailable. Please check the AI engine."

        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }

        try:
            if not stream:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                # Basic mock for stream logic just returning a string for now as fastapi streaming requires specific setup
                response = requests.post(url, json=payload, stream=True)
                response.raise_for_status()
                # For synchronous simple usage, we'll just join the stream chunks
                full_text = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            full_text += chunk["message"]["content"]
                return full_text
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"
