from typing import List
from app.services.ai.assistant.assistant_models import Message

class HistoryFormatter:
    def __init__(self):
        pass

    def format_for_prompt(self, messages: List[Message]) -> str:
        if not messages:
            return "No previous conversation history."
            
        formatted = []
        for msg in messages:
            formatted.append(f"{msg.role.capitalize()}: {msg.content}")
            
        return "\n".join(formatted)