from typing import List, Dict, Any
from ..llm.token_counter import TokenCounter

class ConversationHistory:
    """
    Maintains a rolling conversation history respecting context window limits.
    Automatically trims oldest messages when approaching the model limit.
    """
    def __init__(self, model: str = "llama3", max_turns: int = 20):
        self.model = model
        self.max_turns = max_turns
        self.token_counter = TokenCounter()
        self._history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        self._history.append({"role": role, "content": content})
        self._trim_if_needed()

    def _trim_if_needed(self):
        while len(self._history) > 2 and not self.token_counter.fits_in_context(self._history, self.model):
            # Remove oldest non-system message
            self._history.pop(1 if self._history[0]["role"] == "system" else 0)

    def get_messages(self) -> List[Dict[str, str]]:
        return self._history.copy()

    def clear(self):
        self._history = []