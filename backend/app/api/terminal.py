from fastapi import APIRouter
from pydantic import BaseModel
import subprocess
import shlex

router = APIRouter()


class TerminalRequest(BaseModel):
    command: str


class TerminalResponse(BaseModel):
    success: bool
    output: str


# Allowed commands only
ALLOWED_COMMANDS = [
    "aws",
    "docker",
    "kubectl",
    "terraform",
    "ansible",
    "helm",
    "pwd",
    "ls",
    "cat"
]


@router.post(
    "/execute",
    response_model=TerminalResponse
)
def execute_command(request: TerminalRequest):

    try:
        command = request.command.strip()

        if not command:
            return TerminalResponse(
                success=False,
                output="Command cannot be empty"
            )

        first_word = shlex.split(command)[0]

        if first_word not in ALLOWED_COMMANDS:
            return TerminalResponse(
                success=False,
                output=f"Command '{first_word}' is not allowed"
            )

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        output = ""

        if result.stdout:
            output += result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        return TerminalResponse(
            success=result.returncode == 0,
            output=output if output else "Command completed successfully"
        )

    except subprocess.TimeoutExpired:
        return TerminalResponse(
            success=False,
            output="Command timed out after 60 seconds"
        )

    except Exception as e:
        return TerminalResponse(
            success=False,
            output=str(e)
        )
