from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal, ResourceDB
from app.services.ai.insights import AIInsightEngine
from app.services.ai.chat import CloudAssistant
from app.services.optimization.recommendations import RecommendationEngine
from app.services.cost.aggregator import CostAggregator
from app.services.llm.cloud_chat import CloudLLM

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


# Matching Response Schemas for Client validation compatibility
class LocalAIInsightsResponseSchema(BaseModel):
    executive_summary: str
    risks: List[str]
    savings_opportunities: List[str]
    recommendations: List[str]
    finops_score: int


class LocalAIChatResponseSchema(BaseModel):
    answer: str


@router.get(
    "/ai/insights",
    response_model=LocalAIInsightsResponseSchema
)
@router.get(
    "/api/ai/insights",
    response_model=LocalAIInsightsResponseSchema
)
def insights(db: Session = Depends(get_db)):
    """
    Evaluates resource configurations, waste ratios, and cost streams
    to deliver high-value architectural, security, and financial optimization feedback.
    """
    result = AIInsightEngine.generate(db)
    return result


@router.post(
    "/ai/chat",
    response_model=LocalAIChatResponseSchema
)
# Commented out to resolve conflict with modern Ollama AI chat router:
# @router.post(
#     "/api/ai/chat",
#     response_model=LocalAIChatResponseSchema
# )
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Interactive natural language Copilot chat for cloud topology and FinOps Q&A.
    """
    result = CloudAssistant.ask(db, payload.question)
    return LocalAIChatResponseSchema(answer=result["answer"])


@router.post(
    "/ai/assistant",
    response_model=LocalAIChatResponseSchema
)
@router.post(
    "/api/ai/assistant",
    response_model=LocalAIChatResponseSchema
)
def assistant(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Interactive high-fidelity senior SRE Assistant routing through OpenAI / Gemini API compatibility.
    """
    inventory = db.query(ResourceDB).all()
    recommendations = RecommendationEngine.generate(db)
    costs = CostAggregator.calculate_account_monthly(db, 1)

    answer = CloudLLM.ask(
        inventory=[r.__dict__ for r in inventory],
        costs=costs,
        recommendations=recommendations,
        question=payload.question
    )

    return LocalAIChatResponseSchema(answer=answer)
