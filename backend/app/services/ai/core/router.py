"""
CloudOps AI Router

Exposes the AI pipeline via FastAPI endpoints.
"""

from fastapi import APIRouter

from pydantic import BaseModel

from app.services.ai.core.orchestrator.llm_orchestrator import LLMOrchestrator


router = APIRouter()

orchestrator = LLMOrchestrator()


class AIRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_ai(request: AIRequest):
    """
    Submit a natural language question about your cloud infrastructure.

    Returns intent, topology context, documentation, and AI answer.
    """
    result = orchestrator.ask(request.question)
    return result
