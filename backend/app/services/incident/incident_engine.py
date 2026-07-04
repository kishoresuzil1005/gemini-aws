import logging
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models import ResourceDB

logger = logging.getLogger(__name__)

class IncidentEngine:
    """
    Phase 4 Incident Engine.
    Evaluates rules offline purely against the PostgreSQL Inventory.
    ZERO AWS API CALLS.
    """
    def __init__(self, db: Session):
        self.db = db

    def generate_incidents(self) -> List[Dict[str, Any]]:
        incidents = []
        
        try:
            # Load all resources (or paginate for large environments)
            resources = self.db.query(ResourceDB).all()
            
            for res in resources:
                if res.resource_type == "S3":
                    self._check_s3_rules(res, incidents)
                elif res.resource_type == "IAM":
                    self._check_iam_rules(res, incidents)
                # Add more resource checks here
                
        except Exception as e:
            logger.error(f"Error evaluating incidents: {e}")
            
        return incidents

    def _check_s3_rules(self, res: ResourceDB, incidents: List[Dict[str, Any]]):
        if not res.resource_metadata:
            return
            
        # Example S3 Encryption rule
        # Legacy scanner stored this in metadata (or we mapped it there)
        # Note: AWSDiscoveryScanner's S3 provider will need to capture 'encrypted'
        # Currently we just check the _legacy_configuration_hint if encrypted=False
        is_encrypted = res.resource_metadata.get("encrypted")
        legacy_hint = res.resource_metadata.get("_legacy_configuration_hint", "")
        
        if is_encrypted is False or "Encrypted: False" in str(legacy_hint):
            incidents.append({
                "id": f"inc-s3-enc-{res.resource_id}",
                "resource_id": res.resource_id,
                "title": f"Unencrypted S3 Bucket: {res.name or res.resource_id}",
                "severity": "CRITICAL",
                "description": "Bucket lacks server-side encryption."
            })

    def _check_iam_rules(self, res: ResourceDB, incidents: List[Dict[str, Any]]):
        if not res.resource_metadata:
            return
            
        legacy_hint = res.resource_metadata.get("_legacy_configuration_hint", "")
        if "AdministratorAccess" in str(legacy_hint):
            incidents.append({
                "id": f"inc-iam-admin-{res.resource_id}",
                "resource_id": res.resource_id,
                "title": f"Overly Permissive IAM Role: {res.name or res.resource_id}",
                "severity": "CRITICAL",
                "description": "Role has AdministratorAccess."
            })
