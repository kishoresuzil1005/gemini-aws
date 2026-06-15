from fastapi import APIRouter
from pydantic import BaseModel

from app.services.ai.ollama_service import OllamaService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat(request: ChatRequest):

    response = OllamaService.generate(
        request.message
    )

    return {
        "success": True,
        "response": response
    }
