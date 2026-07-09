from fastapi import APIRouter
from app.core.aws_logger import get_aws_logs, log_aws_call

router = APIRouter(
    tags=["AWS Logs"]
)

@router.get("/api/v1/cloud/logs")
def fetch_aws_logs():
    # Write a quick access audit log
    log_aws_call("logs_api", "fetch_aws_logs", "local", "SUCCESS", "Requested active telemetry stream")
    return get_aws_logs()
