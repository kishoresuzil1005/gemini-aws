"""
Credential Manager — Production Implementation
Handles AWS STS AssumeRole, Azure DefaultCredential, GCP ServiceAccount, and Kubernetes kubeconfig.
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CredentialManager:
    """Resolves credentials across all cloud providers."""

    # ─── AWS ────────────────────────────────────────────────────────────────────

    def get_aws_credentials(
        self,
        role_arn: Optional[str] = None,
        external_id: Optional[str] = None,
        session_name: str = "GeminiCloudSession",
    ) -> Dict[str, str]:
        """
        Returns boto3-compatible credential kwargs.
        If role_arn is given, performs STS AssumeRole; otherwise falls through
        to environment variables, instance profile, or ~/.aws/credentials.
        """
        if role_arn:
            try:
                import boto3
                sts = boto3.client("sts")
                assume_kwargs: Dict[str, Any] = {
                    "RoleArn": role_arn,
                    "RoleSessionName": session_name,
                }
                if external_id:
                    assume_kwargs["ExternalId"] = external_id

                resp = sts.assume_role(**assume_kwargs)
                creds = resp["Credentials"]
                logger.info(f"Assumed role {role_arn} successfully.")
                return {
                    "aws_access_key_id": creds["AccessKeyId"],
                    "aws_secret_access_key": creds["SecretAccessKey"],
                    "aws_session_token": creds["SessionToken"],
                }
            except Exception as e:
                logger.error(f"STS AssumeRole failed for {role_arn}: {e}")
                raise

        # Fall through to boto3 credential chain (env vars / instance profile / ~/.aws)
        return {}

    # ─── AZURE ──────────────────────────────────────────────────────────────────

    def get_azure_credentials(self):
        """
        Returns azure.identity.DefaultAzureCredential.
        Supports: env vars, managed identity, Azure CLI, workload identity.
        """
        try:
            from azure.identity import DefaultAzureCredential
            credential = DefaultAzureCredential()
            logger.info("Azure DefaultAzureCredential resolved.")
            return credential
        except ImportError:
            logger.warning("azure-identity not installed. Run: pip install azure-identity")
            return None
        except Exception as e:
            logger.error(f"Azure credential resolution failed: {e}")
            raise

    # ─── GCP ────────────────────────────────────────────────────────────────────

    def get_gcp_credentials(self, service_account_json_path: Optional[str] = None):
        """
        Returns GCP credentials.
        If a service account JSON path is provided, uses it; otherwise falls back
        to Application Default Credentials (ADC).
        """
        try:
            from google.oauth2 import service_account
            import google.auth

            if service_account_json_path and os.path.exists(service_account_json_path):
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_json_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"],
                )
                logger.info(f"GCP credentials loaded from {service_account_json_path}.")
            else:
                credentials, project = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                logger.info("GCP Application Default Credentials resolved.")

            return credentials
        except ImportError:
            logger.warning("google-auth not installed. Run: pip install google-auth")
            return None
        except Exception as e:
            logger.error(f"GCP credential resolution failed: {e}")
            raise

    # ─── KUBERNETES ─────────────────────────────────────────────────────────────

    def get_kubernetes_credentials(self, kubeconfig_path: Optional[str] = None, in_cluster: bool = False):
        """
        Loads Kubernetes configuration.
        Returns None — the kubernetes SDK uses global state (load_kube_config / load_incluster_config).
        """
        try:
            from kubernetes import config as k8s_config

            if in_cluster:
                k8s_config.load_incluster_config()
                logger.info("Kubernetes in-cluster config loaded.")
            else:
                path = kubeconfig_path or os.environ.get("KUBECONFIG", "~/.kube/config")
                k8s_config.load_kube_config(config_file=os.path.expanduser(path))
                logger.info(f"Kubernetes kubeconfig loaded from {path}.")
        except ImportError:
            logger.warning("kubernetes SDK not installed. Run: pip install kubernetes")
        except Exception as e:
            logger.error(f"Kubernetes credential resolution failed: {e}")
            raise


credential_manager = CredentialManager()