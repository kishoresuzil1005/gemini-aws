from pydantic import BaseModel

class ResolvedResource(BaseModel):
    """Canonical representation of a resource after identifier resolution."""
    resource_id: str
    original_identifier: str
