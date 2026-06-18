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


class RefreshRequest(BaseModel):
    """
    Inventory Refresh Request

    region = all
        -> scan all AWS regions

    region = ap-south-1
        -> scan only Mumbai

    region = us-east-1
        -> scan only Virginia
    """

    region: str = "all"


class RefreshResponse(BaseModel):
    success: bool
    region: str
    message: str
