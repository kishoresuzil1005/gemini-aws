import os
import requests


class EmbeddingService:

    def __init__(self):
        self.model_name = "nomic-embed-text"
        self.dimension = 768
        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://ollama:11434"
        )
        self.session = requests.Session()

    def get_embedding(self, text: str):

        response = self.session.post(
            f"{self.ollama_url}/api/embeddings",
            json={
                "model": self.model_name,
                "prompt": text
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json()["embedding"]

    def get_embeddings(self, texts):

        return [
            self.get_embedding(text)
            for text in texts
        ]

    # --------------------------------------------------
    # Compatibility wrapper
    # --------------------------------------------------

    def embed(self, text: str):
        return self.get_embedding(text)

    def embed_many(self, texts):
        return self.get_embeddings(texts