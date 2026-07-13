from abc import ABC, abstractmethod
from typing import List, Dict, AsyncGenerator, Union
from app.services.ai.assistant.llm.config import AISettings

class BaseProvider(ABC):
    def __init__(self, settings: AISettings):
        self.settings = settings

    @abstractmethod
    def health_check(self) -> bool:
        pass

    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], request_id: str, stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        pas