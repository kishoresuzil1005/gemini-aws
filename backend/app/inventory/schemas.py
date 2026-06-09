from pydantic import BaseModel
from typing import Optional

class ResourceSchema(BaseModel):
    cloud_account_id: int
    provider: str
    resource_type: str
    resource_id: str
    name: Optional[str]
    region: Optional[str]
    status: Optional[str]
    tags: Optional[str]

    class Config:
        from_attributes = True
