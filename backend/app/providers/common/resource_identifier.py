from pydantic import BaseModel
from typing import Optional

class GenericResourceIdentifier(BaseModel):
    """Normalized identifier bridging cloud-specific URIs into a universal AI format."""
    provider: str
    resource_type: str
    resource_name: str
    
    # Optional taxonomy
    region: Optional[str] = None
    zone: Optional[str] = None
    account_id: Optional[str] = None
    project: Optional[str] = None
    subscription: Optional[str] = None
    cluster: Optional[str] = None
    namespace: Optional[str] = None
    
    # The original raw URI
    unique_id: str

    @classmethod
    def parse_aws_arn(cls, arn: str) -> "GenericResourceIdentifier":
        # e.g., arn:aws:ec2:us-east-1:123456789012:instance/i-0abcdef1234567890
        parts = arn.split(":")
        service = parts[2]
        region = parts[3] if len(parts) > 3 and parts[3] else None
        account_id = parts[4] if len(parts) > 4 and parts[4] else None
        
        resource_path = parts[5] if len(parts) > 5 else ""
        res_parts = resource_path.split("/")
        resource_type = res_parts[0] if len(res_parts) > 1 else service
        resource_name = res_parts[-1]
        
        return cls(
            provider="AWS",
            resource_type=resource_type,
            resource_name=resource_name,
            region=region,
            account_id=account_id,
            unique_id=arn
        )
        
    @classmethod
    def parse_azure_id(cls, azure_id: str) -> "GenericResourceIdentifier":
        # /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
        parts = azure_id.strip("/").split("/")
        sub = parts[1] if len(parts) > 1 else None
        
        type_str = parts[-2] if len(parts) > 1 else "unknown"
        name = parts[-1] if len(parts) > 0 else azure_id
        
        return cls(
            provider="AZURE",
            resource_type=type_str,
            resource_name=name,
            subscription=sub,
            unique_id=azure_id
        )
        
    @classmethod
    def parse_gcp_uri(cls, gcp_uri: str) -> "GenericResourceIdentifier":
        # projects/demo/zones/us-central1-a/instances/vm1
        parts = gcp_uri.strip("/").split("/")
        
        parsed = {"projects": None, "zones": None, "regions": None}
        i = 0
        while i < len(parts) - 2:
            key = parts[i]
            if key in parsed and i + 1 < len(parts):
                parsed[key] = parts[i+1]
            i += 2
            
        type_str = parts[-2] if len(parts) > 1 else "unknown"
        name = parts[-1] if len(parts) > 0 else gcp_uri
        
        return cls(
            provider="GCP",
            resource_type=type_str,
            resource_name=name,
            project=parsed.get("projects"),
            zone=parsed.get("zones"),
            region=parsed.get("regions"),
            unique_id=gcp_uri
        )
        
    @classmethod
    def parse_kubernetes_uri(cls, k8s_uri: str) -> "GenericResourceIdentifier":
        # namespaces/default/deployments/payment-service
        parts = k8s_uri.strip("/").split("/")
        ns = None
        type_str = "unknown"
        name = k8s_uri
        
        if "namespaces" in parts:
            idx = parts.index("namespaces")
            if idx + 1 < len(parts):
                ns = parts[idx+1]
            if idx + 2 < len(parts):
                type_str = parts[idx+2]
            if idx + 3 < len(parts):
                name = parts[idx+3]
        elif len(parts) == 2:
            ns = parts[0]
            name = parts[1]
            
        return cls(
            provider="KUBERNETES",
            resource_type=type_str,
            resource_name=name,
            namespace=ns,
            unique_id=k8s_uri
        )
