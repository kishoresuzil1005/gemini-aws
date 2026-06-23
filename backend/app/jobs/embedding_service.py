import requests

class EmbeddingService:

    def __init__(self):
        self.model_name = "nomic-embed-text"
        self.dimension = 768

    def get_embedding(self, text: str):

        response = requests.post(
            "http://ollama:11434/api/embeddings",
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
