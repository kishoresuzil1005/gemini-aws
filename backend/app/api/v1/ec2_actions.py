from fastapi import APIRouter
from pydantic import BaseModel

from app.services.remediation.actions.ec2_actions import EC2Actions
from app.providers.aws.ec2 import EC2Discovery
from app.core.aws_logger import log_aws_call

router = APIRouter()


@router.get("/api/v1/ec2/instances")
def get_ec2_instances(
    region: str
):
    return EC2Discovery.get_instances(region)



class EC2ActionRequest(BaseModel):
    instance_id: str
    account_id: int = 1


@router.post("/api/v1/ec2/start")
def start_ec2(payload: EC2ActionRequest):

    log_aws_call("ec2", "start_instances", "ap-south-1", "SUCCESS", f"Triggered instance START for {payload.instance_id}")

    result = EC2Actions.start_instance(
        payload.account_id,
        payload.instance_id
    )

    return {
        "status": "STARTING",
        "result": result
    }


@router.post("/api/v1/ec2/stop")
def stop_ec2(payload: EC2ActionRequest):

    log_aws_call("ec2", "stop_instances", "ap-south-1", "SUCCESS", f"Triggered instance STOP for {payload.instance_id}")

    result = EC2Actions.stop_instance(
        payload.account_id,
        payload.instance_id
    )

    return {
        "status": "STOPPING",
        "result": result
    }


@router.post("/api/v1/ec2/reboot")
def reboot_ec2(payload: EC2ActionRequest):

    log_aws_call("ec2", "reboot_instances", "ap-south-1", "SUCCESS", f"Triggered instance REBOOT for {payload.instance_id}")

    result = EC2Actions.reboot_instance(
        payload.account_id,
        payload.instance_id
    )

    return {
        "status": "REBOOTING",
        "result": result
    }
