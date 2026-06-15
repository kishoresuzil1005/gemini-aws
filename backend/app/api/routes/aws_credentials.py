from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter()

AWS_DIR = "/shared/aws"

class AWSCredentialsRequest(BaseModel):
    access_key: str
    secret_key: str
    region: str = "us-east-1"


@router.post("/connect")
async def connect_aws(payload: AWSCredentialsRequest):

    os.makedirs(AWS_DIR, exist_ok=True)

    credentials = f"""[default]
aws_access_key_id={payload.access_key}
aws_secret_access_key={payload.secret_key}
"""

    config = f"""[default]
region={payload.region}
output=json
"""

    with open(f"{AWS_DIR}/credentials", "w") as f:
        f.write(credentials)

    with open(f"{AWS_DIR}/config", "w") as f:
        f.write(config)

    return {
        "success": True,
        "message": "AWS credentials saved"
    }
