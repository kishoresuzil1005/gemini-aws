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
from app.services.ai.ec2_relationship_service import EC2RelationshipService
from app.services.ai.vpc_graph_service import VPCGraphService
from app.services.ai.account_topology_service import AccountTopologyService

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

    if (
        "show resources inside vpc" in msg
        or
        "what is deployed in vpc" in msg
        or
        "list resources connected to vpc" in msg
        or
        "show topology for vpc" in msg
    ):
        import re

        match = re.search(
            r"(vpc-[a-z0-9]+)",
            msg
        )

        if not match:
            return {
                "success": False,
                "message": "VPC ID not found"
            }

        vpc_id = match.group(1)

        service = VPCGraphService()
        result = service.get_vpc_graph(
            vpc_id
        )

        return {
            "success": True,
            **result
        }

    if (
        "show vpc for" in msg
        or
        "which vpc contains" in msg
        or
        "which network contains" in msg
    ):
        search_value = (
            msg
                .replace(
                    "show vpc for",
                    ""
                )
                .replace(
                    "which vpc contains",
                    ""
                )
                .replace(
                    "which network contains",
                    ""
                )
                .strip()
        )

        service = EC2RelationshipService()
        result = service.get_instance_vpc(
            search_value
        )

        if not result:
            return {
                "success": False,
                "message": "Instance not found"
            }

        return {
            "success": True,
            "relationship": result
        }

    if (
        "show subnet for" in msg
        or
        "which subnet contains" in msg
        or
        "which subnet is" in msg
    ):
        search_value = (
            msg
                .replace(
                    "show subnet for",
                    ""
                )
                .replace(
                    "which subnet contains",
                    ""
                )
                .replace(
                    "which subnet is",
                    ""
                )
                .replace(
                    "using",
                    ""
                )
                .strip()
        )

        service = EC2RelationshipService()
        result = service.get_instance_subnet(
            search_value
        )

        if not result:
            return {
                "success": False,
                "message": "Instance not found"
            }

        return {
            "success": True,
            "relationship": result
        }

    if (
        "show security groups for" in msg
        or
        "what security groups are attached" in msg
        or
        "describe security groups for" in msg
        or
        "which firewall protects" in msg
    ):
        search_value = (
            msg
                .replace(
                    "show security groups for",
                    ""
                )
                .replace(
                    "what security groups are attached to",
                    ""
                )
                .replace(
                    "what security groups are attached",
                    ""
                )
                .replace(
                    "describe security groups for",
                    ""
                )
                .replace(
                    "which firewall protects",
                    ""
                )
                .strip()
        )

        service = EC2RelationshipService()
        result = service.get_instance_security_groups(
            search_value
        )

        if not result:
            return {
                "success": False,
                "message": "Instance not found"
            }

        return {
            "success": True,
            "relationship": result
        }

    if (
        "explain network path for" in msg
        or
        "show network details for" in msg
        or
        "network path for" in msg
    ):
        search_value = (
            msg
                .replace(
                    "explain network path for",
                    ""
                )
                .replace(
                    "show network details for",
                    ""
                )
                .replace(
                    "network path for",
                    ""
                )
                .strip()
        )

        service = EC2RelationshipService()
        result = service.get_network_path(
            search_value
        )

        if not result:
            return {
                "success": False,
                "message": "Instance not found"
            }

        return {
            "success": True,
            "network_path": result
        }

    if (
        "show my aws topology" in msg
        or
        "show account architecture" in msg
        or
        "show cloud inventory map" in msg
        or
        "summarize my aws account" in msg
    ):
        result = AccountTopologyService.get_account_topology()
        return result


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
    elif intent == Intent.ACCOUNT_TOPOLOGY:
        res = AccountTopologyService.get_account_topology()
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
