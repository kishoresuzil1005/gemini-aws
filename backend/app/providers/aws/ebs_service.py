"""EBS Volume Service — Production"""
import logging
from typing import Any, Dict, List, Optional
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class EbsService:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("ec2", region_name=self.region, role_arn=self.role_arn)

    def list(self) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_volumes")
        volumes = []
        for page in paginator.paginate():
            for vol in page.get("Volumes", []):
                volumes.append({
                    "resource_id": vol["VolumeId"],
                    "resource_type": "EBS",
                    "name": next((t["Value"] for t in vol.get("Tags", []) if t["Key"] == "Name"), vol["VolumeId"]),
                    "region": self.region,
                    "status": vol.get("State", "unknown"),
                    "metadata": {
                        "size_gb": vol.get("Size"),
                        "volume_type": vol.get("VolumeType"),
                        "iops": vol.get("Iops"),
                        "throughput": vol.get("Throughput"),
                        "encrypted": vol.get("Encrypted"),
                        "kms_key_id": vol.get("KmsKeyId"),
                        "availability_zone": vol.get("AvailabilityZone"),
                        "snapshot_id": vol.get("SnapshotId"),
                        "multi_attach_enabled": vol.get("MultiAttachEnabled"),
                        "attachments": [
                            {"instance_id": a["InstanceId"], "device": a["Device"], "state": a["State"]}
                            for a in vol.get("Attachments", [])
                        ],
                        "tags": {t["Key"]: t["Value"] for t in vol.get("Tags", [])},
                    },
                })
        return volumes

    def list_snapshots(self, owner_id: str = "self") -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("describe_snapshots")
        snapshots = []
        for page in paginator.paginate(OwnerIds=[owner_id]):
            for snap in page.get("Snapshots", []):
                snapshots.append({
                    "snapshot_id": snap["SnapshotId"],
                    "volume_id": snap.get("VolumeId"),
                    "state": snap.get("State"),
                    "size_gb": snap.get("VolumeSize"),
                    "start_time": str(snap.get("StartTime", "")),
                    "description": snap.get("Description"),
                    "encrypted": snap.get("Encrypted"),
                })
        return snapshots

    def get(self, resource_id: str) -> Optional[Dict[str, Any]]:
        resp = self._client().describe_volumes(VolumeIds=[resource_id])
        vols = resp.get("Volumes", [])
        return vols[0] if vols else None

    def create(self, availability_zone: str, size_gb: int, volume_type: str = "gp3", encrypted: bool = True, iops: Optional[int] = None, throughput: Optional[int] = None, snapshot_id: Optional[str] = None, tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {
            "AvailabilityZone": availability_zone,
            "Size": size_gb,
            "VolumeType": volume_type,
            "Encrypted": encrypted,
        }
        if iops:
            kwargs["Iops"] = iops
        if throughput:
            kwargs["Throughput"] = throughput
        if snapshot_id:
            kwargs["SnapshotId"] = snapshot_id
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "volume", "Tags": tags}]
        return self._client().create_volume(**kwargs)

    def attach(self, volume_id: str, instance_id: str, device: str) -> Dict[str, Any]:
        return self._client().attach_volume(VolumeId=volume_id, InstanceId=instance_id, Device=device)

    def detach(self, volume_id: str, instance_id: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VolumeId": volume_id, "Force": force}
        if instance_id:
            kwargs["InstanceId"] = instance_id
        return self._client().detach_volume(**kwargs)

    def create_snapshot(self, volume_id: str, description: str = "", tags: Optional[List] = None) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {"VolumeId": volume_id, "Description": description}
        if tags:
            kwargs["TagSpecifications"] = [{"ResourceType": "snapshot", "Tags": tags}]
        return self._client().create_snapshot(**kwargs)

    def delete_snapshot(self, snapshot_id: str) -> Dict[str, Any]:
        self._client().delete_snapshot(SnapshotId=snapshot_id)
        return {"status": "deleted", "snapshot_id": snapshot_id}

    def delete(self, resource_id: str) -> Dict[str, Any]:
        self._client().delete_volume(VolumeId=resource_id)
        return {"status": "deleted", "resource_id": resource_id}
