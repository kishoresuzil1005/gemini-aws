import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self.dimension = 384
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            print(f"[EMBEDDING SERVICE WARNING] SentenceTransformer not available, using fallback: {e}")

    def get_embedding(self, text: str) -> list:
        if self.model is not None:
            try:
                embeddings = self.model.encode(text)
                return embeddings.tolist()
            except Exception as e:
                print(f"[EMBEDDING ERROR] Failed to encode text: {e}. Falling back to deterministic numeric generation.")
        
        # Fallback deterministic embedder
        return self._fallback_embedding(text)

    def get_embeddings(self, texts: list) -> list:
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            except Exception as e:
                print(f"[EMBEDDING ERROR] Failed to encode text list: {e}. Falling back.")
        
        return [self._fallback_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> list:
        # Deterministic generation using basic hashing of text to avoid random fluctuation
        state = 0
        for char in text:
            state = (state * 31 + ord(char)) & 0xFFFFFFFF
        
        # Generate pseudo-random vector based on seed state
        np.random.seed(state)
        vec = np.random.normal(0.0, 1.0, self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
