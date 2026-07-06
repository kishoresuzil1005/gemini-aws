from app.services.ai.assistant.llm_provider import LLMProvider
from app.services.ai.assistant.prompt_templates import SYSTEM_PROMPT, build_user_prompt

class ResponseGenerator:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def generate(self, question: str, history_str: str, context_str: str) -> str:
        prompt = build_user_prompt(question, history_str, context_str)
        return self.provider.generate_response(prompt=prompt, system_prompt=SYSTEM_PROMPT)
