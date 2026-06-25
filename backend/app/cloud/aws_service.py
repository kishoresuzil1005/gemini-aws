import boto3
import logging

logger = logging.getLogger("AwsService")

class AwsService:
    @staticmethod
    def assume_role(role_arn: str, external_id: str | None):
        try:
            sts = boto3.client("sts")
            params = {
                "RoleArn": role_arn,
                "RoleSessionName": "cloudops"
            }
            if external_id:
                params["ExternalId"] = external_id
            response = sts.assume_role(**params)
            creds = response["Credentials"]
            return {
                "access_key": creds["AccessKeyId"],
                "secret_key": creds["SecretAccessKey"],
                "session_token": creds["SessionToken"],
                "success": True
            }
        except Exception as e:
            logger.warning(f"Failed to assume role {role_arn} natively: {e}. Returning dummy fallback credentials.")
            return {
                "access_key": "dummy_access_key",
                "secret_key": "dummy_secret_key",
                "session_token": "dummy_session_token",
                "success": False
            }
