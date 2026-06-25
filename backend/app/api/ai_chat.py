from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai.rag_service import RAGService

router = APIRouter()

rag = RAGService()


class AIChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: AIChatRequest):

    try:

        result = rag.query_rag(
            request.question
        )

        return {
            "success": True,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
