from fastapi import FastAPI
from pydantic import BaseModel
import subprocess

app = FastAPI(title="CloudShell Service")

class CommandRequest(BaseModel):
    command: str


@app.post("/execute")
async def execute(req: CommandRequest):

    try:
        result = subprocess.run(
            req.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
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
