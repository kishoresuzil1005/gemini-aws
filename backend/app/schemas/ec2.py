from pydantic import BaseModel
from typing import Optional


class EC2InstanceSchema(BaseModel):
    instance_id: str
    instance_type: str
    state: str
    region: str
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
