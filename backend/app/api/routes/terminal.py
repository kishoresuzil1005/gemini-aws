from fastapi import APIRouter
from pydantic import BaseModel
import requests

router = APIRouter()

class CommandRequest(BaseModel):
    command: str


@router.post("/execute")
async def execute_command(req: CommandRequest):
    try:
        response = requests.post(
            "http://cloudshell:9000/execute",
            json={
                "command": req.command
            },
            timeout=180
        )
        return response.json()

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

