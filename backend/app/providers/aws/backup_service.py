"""AWS Backup Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class BackupService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("backup", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        return self.list_vaults()

    def list_vaults(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("list_backup_vaults")
        vaults = []
        for page in paginator.paginate():
            for vault in page.get("BackupVaultList", []):
                vaults.append({
                    "resource_id": vault.get("BackupVaultArn", vault.get("BackupVaultName")),
                    "resource_type": "BackupVault",
                    "name": vault.get("BackupVaultName"),
                    "region": self.region,
                    "status": "active",
                    "metadata": {
                        "number_of_recovery_points": vault.get("NumberOfRecoveryPoints"),
                        "encryption_key_arn": vault.get("EncryptionKeyArn"),
                        "creation_date": str(vault.get("CreationDate", "")),
                    },
                })
        return vaults

    def list_plans(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("list_backup_plans")
        plans = []
        for page in paginator.paginate():
            plans.extend(page.get("BackupPlansList", []))
        return plans

    def list_jobs(self, state: Optional[str] = None) -> List[Dict[str, Any]]:
        kwargs: Dict[str, Any] = {}
        if state:
            kwargs["ByState"] = state
        paginator = self._client().get_paginator("list_backup_jobs")
        jobs = []
        for page in paginator.paginate(**kwargs):
            for job in page.get("BackupJobs", []):
                jobs.append({
                    "job_id": job.get("BackupJobId"),
                    "state": job.get("State"),
                    "resource_arn": job.get("ResourceArn"),
                    "resource_type": job.get("ResourceType"),
                    "vault_name": job.get("BackupVaultName"),
                    "percent_done": job.get("PercentDone"),
                    "backup_size_bytes": job.get("BackupSizeInBytes"),
                    "creation_date": str(job.get("CreationDate", "")),
                    "completion_date": str(job.get("CompletionDate", "")),
                })
        return jobs

    def start_backup_job(self, vault_name: str, resource_arn: str, iam_role_arn: str, lifecycle: Optional[Dict] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "BackupVaultName": vault_name,
            "ResourceArn": resource_arn,
            "IamRoleArn": iam_role_arn,
        }
        if lifecycle:
            kwargs["Lifecycle"] = lifecycle
        resp = self._client().start_backup_job(**kwargs)
        return {
            "backup_job_id": resp.get("BackupJobId"),
            "creation_date": str(resp.get("CreationDate", "")),
            "status": "started",
        }

    def list_recovery_points(self, vault_name: str) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("list_recovery_points_by_backup_vault")
        points = []
        for page in paginator.paginate(BackupVaultName=vault_name):
            points.extend(page.get("RecoveryPoints", []))
        return points

    def create_vault(self, vault_name: str, kms_key_id: Optional[str] = None, tags: Optional[Dict] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"BackupVaultName": vault_name}
        if kms_key_id:
            kwargs["EncryptionKeyArn"] = kms_key_id
        if tags:
            kwargs["BackupVaultTags"] = tags
        resp = self._client().create_backup_vault(**kwargs)
        return {"vault_arn": resp.get("BackupVaultArn"), "status": "created"}
