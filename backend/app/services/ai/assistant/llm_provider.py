from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator, Union

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[str, AsyncGenerator[str, None]]:
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        pass
