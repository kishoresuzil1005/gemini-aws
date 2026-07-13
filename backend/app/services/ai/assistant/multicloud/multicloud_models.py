from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel

class CloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"
    KUBERNETES = "KUBERNETES"
    VMWARE = "VMWARE"
    OCI = "OCI"

class GenericResourceType(str, Enum):
    COMPUTE = "compute"
    STORAGE = "storage"
    DATABASE = "database"
    NETWORK = "network"
    KUBERNETES = "kubernetes"
    SECURITY = "security"
    LOAD_BALANCER = "LOAD_BALANCER"
    FUNCTION = "FUNCTION"
    CONTAINER = "CONTAINER"
    CLUSTER = "CLUSTER"
    CACHE = "CACHE"
    DNS = "DNS"
    IDENTITY = "IDENTITY"

class GenericAction(str, Enum):
    START = "START"
    STOP = "STOP"
    RESTART = "RESTART"
    CREATE = "CREATE"
    DELETE = "DELETE"
    RESIZE = "RESIZE"
    BACKUP = "BACKUP"

class GenericActionRequest(BaseModel):
    action: GenericAction
    resource_type: GenericResourceType
    resource_id: str
    parameters: Dict[str, Any] = {}

class TranslatedActionPayload(BaseModel):
    provider: CloudProvider
    api_call: str
    payload: Dict[str, Any]