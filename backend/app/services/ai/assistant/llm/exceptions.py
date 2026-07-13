class LlmException(Exception):
    """Base exception for LLM operations."""
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.message = message
        self.retryable = retryable

class LlmConnectionError(LlmException):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)

class LlmTimeoutError(LlmException):
    def __init__(self, message: str):
        super().__init__(message, retryable=True)

class LlmProviderError(LlmException):
    def __init__(self, message: str):
        super().__init__(message, retryable=False)