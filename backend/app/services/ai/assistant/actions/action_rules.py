from typing import Dict, Any

# Example rules configuration. In a real system, this would be loaded from a DB or YAML.
ACTION_POLICIES = {
    "DELETE_RDS": {
        "requires_approval": True,
        "rollback_possible": False,
        "allowed_in_production": False,
        "max_retries": 0,
        "timeout_seconds": 300,
        "risk_level": "CRITICAL"
    },
    "STOP_EC2": {
        "requires_approval": True,
        "rollback_possible": True,
        "allowed_in_production": True,
        "max_retries": 3,
        "timeout_seconds": 60,
        "risk_level": "HIGH"
    },
    "RESTART_EC2": {
        "requires_approval": False,
        "rollback_possible": False,
        "allowed_in_production": True,
        "max_retries": 3,
        "timeout_seconds": 60,
        "risk_level": "LOW"
    },
    "RESIZE_EBS": {
        "requires_approval": True,
        "rollback_possible": True,
        "allowed_in_production": True,
        "max_retries": 1,
        "timeout_seconds": 120,
        "risk_level": "MEDIUM"
    },
    "DESCRIBE_EC2": {
        "requires_approval": False,
        "rollback_possible": False,
        "allowed_in_production": True,
        "max_retries": 3,
        "timeout_seconds": 10,
        "risk_level": "INFO"
    }
}
