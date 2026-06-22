from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai.chat import CloudAssistant
from app.services.ai.ollama_service import OllamaService
from app.services.ai.inventory_ai import (
    InventoryAIService
)
from app.services.ai.rds_inventory import (
    RDSInventoryService
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    CloudOps AI Copilot

    Priority:
    1. Direct AWS Inventory & Custom EC2 Intent Checks
    2. CloudAssistant (live cloud intelligence)
    3. Ollama fallback
    """

    message = request.message.lower()

    if "ec2" in message and (
        "how many" in message
        or "count" in message
    ):
        instances = (
            InventoryAIService
            .get_all_ec2_instances()
        )

        running = len([
            x for x in instances
            if x["state"] == "running"
        ])

        stopped = len([
            x for x in instances
            if x["state"] == "stopped"
        ])

        return {
            "success": True,
            "response":
                f"You currently have "
                f"{len(instances)} EC2 instances. "
                f"{running} are running and "
                f"{stopped} are stopped."
        }

    if (
        "running" in message
        and "instance" in message
    ):
        instances = (
            InventoryAIService
            .get_all_ec2_instances()
        )

        running = [
            i
            for i in instances
            if i["state"] == "running"
        ]

        return {
            "success": True,
            "total": len(running),
            "instances": running
        }

    if (
        "stopped" in message
        and "instance" in message
    ):
        instances = (
            InventoryAIService
            .get_all_ec2_instances()
        )

        stopped = [
            i
            for i in instances
            if i["state"] == "stopped"
        ]

        return {
            "success": True,
            "total": len(stopped),
            "instances": stopped
        }

    if (
        "list" in message
        and "ec2" in message
    ):
        instances = (
            InventoryAIService
            .get_all_ec2_instances()
        )

        return {
            "success": True,
            "total": len(instances),
            "instances": instances
        }

    if (
        "show" in message
        and "instance" in message
    ):
        instances = (
            InventoryAIService
            .get_all_ec2_instances()
        )

        return {
            "success": True,
            "instances": instances
        }

    if (
        "rds" in message
        and "how many" in message
    ):

        databases = (
            RDSInventoryService
            .get_all_rds()
        )

        return {

            "success": True,

            "response":
                f"You currently have "
                f"{len(databases)} "
                f"RDS databases."
        }

    if (
        "list" in message
        and "rds" in message
    ):

        databases = (
            RDSInventoryService
            .get_all_rds()
        )

        return {

            "success": True,

            "total":
                len(databases),

            "databases":
                databases
        }

    if (
        "postgres" in message
    ):

        databases = (
            RDSInventoryService
            .get_all_rds()
        )

        postgres = [

            db

            for db in databases

            if "postgres"
            in db["engine"]
        ]

        return {

            "success": True,

            "total":
                len(postgres),

            "databases":
                postgres
        }

    if (
        "mysql" in message
    ):

        databases = (
            RDSInventoryService
            .get_all_rds()
        )

        mysql = [

            db

            for db in databases

            if "mysql"
            in db["engine"]
        ]

        return {

            "success": True,

            "total":
                len(mysql),

            "databases":
                mysql
        }

    try:

        result = CloudAssistant.ask(
            db,
            request.message
        )

        if result and result.get("answer"):

            return {
                "success": True,
                "response": result["answer"]
            }

    except Exception as e:

        print(
            f"[AI ROUTER] CloudAssistant failed: {e}"
        )

    # Fallback to Ollama
    response = OllamaService.generate(
        request.message
    )

    return {
        "success": True,
        "response": response
    }
