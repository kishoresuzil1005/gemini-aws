from typing import Dict, List

class TokenCounter:
    """
    Estimates token usage to prevent context window overflow.
    """
    # Rough approximation: 1 token ≈ 4 characters
    CHARS_PER_TOKEN = 4

    CONTEXT_LIMITS = {
        "llama3": 8192,
        "qwen2": 32768,
        "deepseek-coder": 16384,
        "mistral": 8192,
    }

    def count(self, text: str) -> int:
        return max(1, len(text) // self.CHARS_PER_TOKEN)

    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        return sum(self.count(m.get("content", "")) for m in messages)

    def fits_in_context(self, messages: List[Dict[str, str]], model: str) -> bool:
        limit = self.CONTEXT_LIMITS.get(model, 8192)
        used = self.count_messages(messages)
        fits = used < limit
        print(f"[TokenCounter] {used}/{limit} tokens for model '{model}' — {'OK' if fits else 'OVERFLOW'}")
        return fit