from typing import List, Dict, Any, Optional
from app.services.ai.assistant.llm.base_provider import BaseProvider
from app.services.ai.assistant.assistant_models import ChatResponse

class FakeProvider(BaseProvider):
    def __init__(self, response_text="This is a mocked AI response."):
        self.response_text = response_text

    def generate_response(self, messages: List[Dict[str, str]], request_id: str, stream: bool = False, callbacks=None) -> str:
        return self.response_text

    def validate_connection(self) -> bool:
        return True

    def health_check(self) -> dict:
        return {"status": "healthy"}
