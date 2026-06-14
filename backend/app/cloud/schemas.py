from pydantic import BaseModel
from typing import Optional

class AwsConnectRequest(BaseModel):
    account_name: str
    account_id: str
    role_arn: str
    external_id: Optional[str] = None
