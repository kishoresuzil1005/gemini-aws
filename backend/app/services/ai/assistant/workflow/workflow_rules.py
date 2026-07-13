# Configuration for specific complex operational workflows

WORKFLOW_POLICIES = {
    "UPGRADE_EKS_CLUSTER": {
        "max_duration_seconds": 7200,
        "allowed_concurrency": 1,
        "requires_compensation_plan": True,
        "blackout_windows": [
            # e.g., "Friday 18:00 - Sunday 23:59"
        ]
    },
    "REMEDIATE_COMPROMISED_EC2": {
        "max_duration_seconds": 600,
        "allowed_concurrency": 5,
        "requires_compensation_plan": False,
        "blackout_windows": [] # Security workflows ignore blackout windows
    },
    "BULK_RESIZE_EBS": {
        "max_duration_seconds": 3600,
        "allowed_concurrency": 10,
        "requires_compensation_plan": True,
        "blackout_windows": []
    }
