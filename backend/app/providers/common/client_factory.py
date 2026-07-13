"""
Client Factory — Production Implementation
Central factory for all SDK clients: boto3, Azure, GCP, Kubernetes.
"""
import logging
import os
import threading
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ClientFactory:
    """
    Central factory for all cloud SDK clients.
    - Caches clients per (service, region) to reuse TCP connections.
    - Thread-safe via per-key locking.
    """

    def __init__(self):
        self._clients: Dict[str, Any] = {}
        self._lock = threading.Lock()

    # ─── AWS ────────────────────────────────────────────────────────────────────

    def get_aws_client(
        self,
        service_name: str,
        region_name: Optional[str] = None,
        role_arn: Optional[str] = None,
        external_id: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ) -> Any:
        """
        Returns a boto3 client for the specified AWS service.
        If role_arn is given, assumes that role via STS first.
        """
        import boto3
        from botocore.config import Config

        region = region_name or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
        cache_key = f"aws_{service_name}_{region}_{role_arn}"

        with self._lock:
            if cache_key not in self._clients:
                session_kwargs: Dict[str, Any] = {}

                if role_arn:
                    from app.providers.common.credential_manager import credential_manager
                    creds = credential_manager.get_aws_credentials(
                        role_arn=role_arn, external_id=external_id
                    )
                    session_kwargs.update(creds)

                retry_config = Config(
                    retries={"max_attempts": 5, "mode": "adaptive"},
                    connect_timeout=10,
                    read_timeout=30,
                )

                client_kwargs: Dict[str, Any] = {
                    "region_name": region,
                    "config": retry_config,
                }
                if endpoint_url:
                    client_kwargs["endpoint_url"] = endpoint_url
                client_kwargs.update(session_kwargs)

                self._clients[cache_key] = boto3.client(service_name, **client_kwargs)
                logger.debug(f"Created boto3 client: {service_name} in {region}")

        return self._clients[cache_key]

    # ─── AZURE ──────────────────────────────────────────────────────────────────

    def get_azure_client(
        self,
        client_class: Any,
        subscription_id: str,
        credential: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """
        Returns an Azure management SDK client.
        Example: get_azure_client(ComputeManagementClient, subscription_id)
        """
        cache_key = f"azure_{client_class.__name__}_{subscription_id}"
        with self._lock:
            if cache_key not in self._clients:
                if credential is None:
                    from app.providers.common.credential_manager import credential_manager
                    credential = credential_manager.get_azure_credentials()

                self._clients[cache_key] = client_class(credential, subscription_id, **kwargs)
                logger.debug(f"Created Azure client: {client_class.__name__}")

        return self._clients[cache_key]

    # ─── GCP ────────────────────────────────────────────────────────────────────

    def get_gcp_client(
        self,
        client_class: Any,
        project_id: Optional[str] = None,
        credentials: Optional[Any] = None,
        **kwargs,
    ) -> Any:
        """
        Returns a GCP client instance.
        Example: get_gcp_client(compute_v1.InstancesClient)
        """
        cache_key = f"gcp_{client_class.__name__}_{project_id}"
        with self._lock:
            if cache_key not in self._clients:
                if credentials is None:
                    from app.providers.common.credential_manager import credential_manager
                    credentials = credential_manager.get_gcp_credentials()

                self._clients[cache_key] = client_class(credentials=credentials, **kwargs)
                logger.debug(f"Created GCP client: {client_class.__name__}")

        return self._clients[cache_key]

    # ─── KUBERNETES ─────────────────────────────────────────────────────────────

    def get_kubernetes_client(
        self,
        api_class: Any,
        kubeconfig_path: Optional[str] = None,
        in_cluster: bool = False,
    ) -> Any:
        """
        Returns a Kubernetes API client (e.g. CoreV1Api, AppsV1Api).
        Example: get_kubernetes_client(client.AppsV1Api)
        """
        cache_key = f"k8s_{api_class.__name__}_{kubeconfig_path}_{in_cluster}"
        with self._lock:
            if cache_key not in self._clients:
                from app.providers.common.credential_manager import credential_manager
                credential_manager.get_kubernetes_credentials(
                    kubeconfig_path=kubeconfig_path, in_cluster=in_cluster
                )
                self._clients[cache_key] = api_class()
                logger.debug(f"Created Kubernetes client: {api_class.__name__}")

        return self._clients[cache_key]

    def invalidate(self, cache_key: str):
        """Remove a cached client (e.g., after credential rotation)."""
        with self._lock:
            self._clients.pop(cache_key, None)

    def clear(self):
        """Remove all cached clients."""
        with self._lock:
            self._clients.clear()


client_factory = ClientFactory()