from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.ai.chat import CloudAssistant
from app.services.ai.ollama_service import OllamaService
from app.ai.intents import Intent
from app.ai.router import IntentRouter
from app.services.ai.ec2_service import EC2Service
from app.services.ai.rds_service import RDSService
from app.services.ai.s3_service import S3Service
from app.services.ai.vpc_service import VPCService
from app.services.ai.subnet_service import SubnetService
from app.services.aws.security_group_service import SecurityGroupService
from app.services.aws.security_audit_service import SecurityAuditService
from app.services.exposure_service import ExposureService

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

    message = request.message
    msg = message.lower()

    intent = IntentRouter.classify(msg)

    res = None
    if intent == Intent.EC2:
        res = EC2Service.handle(msg)
    elif intent == Intent.RDS:
        res = RDSService.handle(msg)
    elif intent == Intent.S3:
        res = S3Service.handle(msg)
    elif intent == Intent.VPC:
        res = VPCService.handle(msg)
    elif intent == Intent.SUBNET:
        res = SubnetService.handle(msg)
    elif intent == Intent.SECURITY_GROUP:
        res = SecurityGroupService.handle(msg)
    elif intent == Intent.SECURITY_AUDIT:
        res = SecurityAuditService.handle(msg)
    elif intent == Intent.PUBLIC_EXPOSURE:
        instances = ExposureService.get_public_instances()
        res = {
            "success": True,
            "total": len(instances),
            "instances": instances
        }

    if res is not None:
        return res

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
