from typing import List, Dict

class MemoryManager:
    def __init__(self):
        # In a real system, this would be backed by Redis or a DB keyed by session_id
        self._history: Dict[str, List[Dict[str, str]]] = {}
        self._context: Dict[str, Dict[str, str]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._history.get(session_id, [])

    def clear_history(self, session_id: str):
        if session_id in self._history:
            self._history[session_id] = []
        if session_id in self._context:
            self._context[session_id] = {}

    def update_context(self, session_id: str, key: str, value: str):
        if session_id not in self._context:
            self._context[session_id] = {}
        self._context[session_id][key] = value

    def get_context(self, session_id: str) -> Dict[str, str]:
        return self._context.get(session_id, {})
