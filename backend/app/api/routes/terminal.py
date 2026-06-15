from fastapi import APIRouter
from pydantic import BaseModel
import subprocess

router = APIRouter()

class CommandRequest(BaseModel):
    command: str


@router.post("/execute")
async def execute_command(req: CommandRequest):
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "cloudshell",
                "bash",
                "-c",
                req.command
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
