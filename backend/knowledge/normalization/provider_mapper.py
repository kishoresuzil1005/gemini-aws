# knowledge/normalization/provider_mapper.py
"""Translates provider-specific taxonomy to universal taxonomy."""

from typing import Dict, Tuple, Type
from .normalization_models import CanonicalModel, CloudComputeInstance, ObjectStorageBucket, IdentityRole, MonitoringMetric, SecurityControl

class ProviderMapper:
    """Translates provider-specific raw terminology into Canonical terms."""

    def __init__(self):
        # Maps (provider, resource_type) -> (CanonicalClass, default_mapping_dict)
        self.mappings: Dict[Tuple[str, str], Tuple[Type[CanonicalModel], Dict[str, str]]] = {
            ("aws", "AWS::EC2::Instance"): (CloudComputeInstance, {"name": "resource_name", "instance_type": "InstanceType"}),
            ("aws", "AWS::S3::Bucket"): (ObjectStorageBucket, {"name": "resource_name"}),
            ("aws", "AWS::IAM::Role"): (IdentityRole, {"name": "resource_name"}),
            # Pseudo-types from extractors
            ("aws", "CloudWatchMetric"): (MonitoringMetric, {"name": "metric_name", "namespace": "namespace"}),
            ("aws", "SecurityHubControl"): (SecurityControl, {"name": "title", "severity": "Severity"}),
        }

    def get_mapping(self, provider: str, candidate_type: str) -> Tuple[Type[CanonicalModel], Dict[str, str]]:
        """Returns the canonical class and field translation map for a given provider type."""
        key = (provider.lower(), candidate_type)
        return self.mappings.get(key, (CanonicalModel, {"name": "candidate_id"}))
