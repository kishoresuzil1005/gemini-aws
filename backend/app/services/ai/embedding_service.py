import requests
import numpy as np

class EmbeddingService:
    def __init__(self):
        self.model_name = "nomic-embed-text"
        self.dimension = 768

    def get_embedding(self, text: str):
        try:
            response = requests.post(
                "http://ollama:11434/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()["embedding"]
        except Exception as e:
            print(f"[Ollama Embedding Warning] Connection failed, using deterministic fallback: {e}")
            return self._fallback_embedding(text)

    def get_embeddings(self, texts):
        return [
            self.get_embedding(t)
            for t in texts
        ]

    def _fallback_embedding(self, text: str) -> list:
        # Deterministic generation using basic hashing of text
        state = 0
        for char in text:
            state = (state * 31 + ord(char)) & 0xFFFFFFFF
        
        # Generate pseudo-random vector of dimension 768 based on seed state
        np.random.seed(state)
        vec = np.random.normal(0.0, 1.0, self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
