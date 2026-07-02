import time
from typing import Dict

from app.ai.context.context_builder import ContextBuilder
from app.ai.prompt.prompt_builder import PromptBuilder
from app.ai.services.ollama_service import OllamaService


class LLMOrchestrator:

    def __init__(self):

        self.context_builder = ContextBuilder()

        self.prompt_builder = PromptBuilder()

        self.llm = OllamaService()

    def ask(
        self,
        question: str
    ) -> Dict:

        # --- Context ---
        start = time.time()
        context = self.context_builder.build(question)
        context_time = time.time() - start

        # --- Prompt ---
        start = time.time()
        prompt = self.prompt_builder.build(context)
        prompt_time = time.time() - start

        # --- LLM ---
        start = time.time()
        response = self.llm.chat(
            system=prompt["system"],
            prompt=prompt["user"]
        )
        llm_time = time.time() - start

        return {
            "question": question,
            "answer": response,
            "model": self.llm.model_name,
            "context": context,
            "timing": {
                "context": round(context_time, 3),
                "prompt": round(prompt_time, 3),
                "llm": round(llm_time, 3)
            },
            "metadata": {
                "resources_used": len(context.get("resources", [])),
                "documents_used": len(context.get("documents", []))
            }
        }

    def close(self):

        self.context_builder.close()
