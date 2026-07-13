"""S3 Service — Production (full implementation)"""
import json
import logging
from typing import Any, Dict, List, Optional
from botocore.exceptions import ClientError
from app.providers.common.client_factory import client_factory

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, region: str = "us-east-1", role_arn: Optional[str] = None):
        self.region = region
        self.role_arn = role_arn

    def _client(self):
        return client_factory.get_aws_client("s3", region_name=self.region, role_arn=self.role_arn)

    # ─── Buckets ──────────────────────────────────────────────────────────────────

    def list_buckets(self) -> List[Dict[str, Any]]:
        resp = self._client().list_buckets()
        buckets = []
        for bucket in resp.get("Buckets", []):
            name = bucket["Name"]
            try:
                location = self._client().get_bucket_location(Bucket=name).get("LocationConstraint") or "us-east-1"
            except ClientError:
                location = "unknown"
            buckets.append({
                "resource_id": name,
                "resource_type": "S3",
                "name": name,
                "region": location,
                "status": "active",
                "metadata": {"creation_date": str(bucket.get("CreationDate", ""))},
            })
        return buckets

    def get_bucket(self, bucket_name: str) -> Dict[str, Any]:
        client = self._client()
        result: Dict[str, Any] = {"name": bucket_name}

        # Versioning
        try:
            result["versioning"] = client.get_bucket_versioning(Bucket=bucket_name).get("Status", "Disabled")
        except ClientError:
            result["versioning"] = "unknown"

        # Encryption
        try:
            enc = client.get_bucket_encryption(Bucket=bucket_name)
            result["encryption"] = enc.get("ServerSideEncryptionConfiguration", {})
        except ClientError:
            result["encryption"] = None

        # Public Access Block
        try:
            pab = client.get_public_access_block(Bucket=bucket_name)
            result["public_access_block"] = pab.get("PublicAccessBlockConfiguration", {})
        except ClientError:
            result["public_access_block"] = {}

        # Lifecycle
        try:
            lc = client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            result["lifecycle_rules"] = lc.get("Rules", [])
        except ClientError:
            result["lifecycle_rules"] = []

        # Logging
        try:
            log_resp = client.get_bucket_logging(Bucket=bucket_name)
            result["logging"] = log_resp.get("LoggingEnabled", {})
        except ClientError:
            result["logging"] = {}

        # Tags
        try:
            tags_resp = client.get_bucket_tagging(Bucket=bucket_name)
            result["tags"] = {t["Key"]: t["Value"] for t in tags_resp.get("TagSet", [])}
        except ClientError:
            result["tags"] = {}

        return result

    def create_bucket(self, bucket_name: str, region: Optional[str] = None) -> Dict[str, Any]:
        target_region = region or self.region
        kwargs: Dict[str, Any] = {"Bucket": bucket_name}
        if target_region != "us-east-1":
            kwargs["CreateBucketConfiguration"] = {"LocationConstraint": target_region}
        self._client().create_bucket(**kwargs)
        return {"status": "created", "bucket": bucket_name, "region": target_region}

    def delete_bucket(self, bucket_name: str) -> Dict[str, Any]:
        self._client().delete_bucket(Bucket=bucket_name)
        return {"status": "deleted", "bucket": bucket_name}

    # ─── Objects ──────────────────────────────────────────────────────────────────

    def list_objects(self, bucket_name: str, prefix: str = "", max_keys: int = 1000) -> List[Dict[str, Any]]:
        paginator = self._client().get_paginator("list_objects_v2")
        objects = []
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in page.get("Contents", []):
                objects.append({
                    "key": obj["Key"],
                    "size_bytes": obj.get("Size"),
                    "last_modified": str(obj.get("LastModified", "")),
                    "storage_class": obj.get("StorageClass"),
                    "etag": obj.get("ETag", "").strip('"'),
                })
        return objects

    def upload_object(self, bucket_name: str, key: str, body: bytes, content_type: str = "application/octet-stream", server_side_encryption: str = "AES256") -> Dict[str, Any]:
        self._client().put_object(
            Bucket=bucket_name, Key=key, Body=body,
            ContentType=content_type, ServerSideEncryption=server_side_encryption,
        )
        return {"status": "uploaded", "bucket": bucket_name, "key": key}

    def download_object(self, bucket_name: str, key: str) -> bytes:
        resp = self._client().get_object(Bucket=bucket_name, Key=key)
        return resp["Body"].read()

    def delete_object(self, bucket_name: str, key: str) -> Dict[str, Any]:
        self._client().delete_object(Bucket=bucket_name, Key=key)
        return {"status": "deleted", "bucket": bucket_name, "key": key}

    # ─── Policy ───────────────────────────────────────────────────────────────────

    def get_bucket_policy(self, bucket_name: str) -> Optional[Dict[str, Any]]:
        try:
            resp = self._client().get_bucket_policy(Bucket=bucket_name)
            return json.loads(resp.get("Policy", "{}"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchBucketPolicy":
                return None
            raise

    def put_bucket_policy(self, bucket_name: str, policy: Dict[str, Any]) -> Dict[str, Any]:
        self._client().put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
        return {"status": "policy_applied", "bucket": bucket_name}

    def delete_bucket_policy(self, bucket_name: str) -> Dict[str, Any]:
        self._client().delete_bucket_policy(Bucket=bucket_name)
        return {"status": "policy_deleted", "bucket": bucket_name}

    # ─── Versioning ───────────────────────────────────────────────────────────────

    def enable_versioning(self, bucket_name: str) -> Dict[str, Any]:
        self._client().put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={"Status": "Enabled"},
        )
        return {"status": "versioning_enabled", "bucket": bucket_name}

    def list_object_versions(self, bucket_name: str, prefix: str = "") -> Dict[str, Any]:
        resp = self._client().list_object_versions(Bucket=bucket_name, Prefix=prefix)
        return {
            "versions": resp.get("Versions", []),
            "delete_markers": resp.get("DeleteMarkers", []),
        }

    # Backward compat alias
    def list(self) -> List[Dict[str, Any]]:
        return self.list_buckets()
