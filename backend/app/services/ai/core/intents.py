"""
CloudOps AI Intent Definitions

This module defines the high-level intent categories understood by the
CloudOps AI platform.

The Intent Classifier maps user requests into one of these categories
before the Cloud Context Builder retrieves infrastructure data.
"""

from enum import Enum


class Intent(str, Enum):
    """
    High-level AI intents.
    """

    # ---------------------------------------------------------
    # Infrastructure
    # ---------------------------------------------------------

    INVENTORY = "inventory"

    TOPOLOGY = "topology"

    RESOURCE_DETAILS = "resource_details"

    # ---------------------------------------------------------
    # Operations
    # ---------------------------------------------------------

    MONITORING = "monitoring"

    DIAGNOSIS = "diagnosis"

    ROOT_CAUSE = "root_cause"

    PERFORMANCE = "performance"

    INCIDENT = "incident"

    HEALTH = "health"

    # ---------------------------------------------------------
    # Security
    # ---------------------------------------------------------

    SECURITY = "security"

    COMPLIANCE = "compliance"

    PUBLIC_EXPOSURE = "public_exposure"

    IAM = "iam"

    # ---------------------------------------------------------
    # FinOps
    # ---------------------------------------------------------

    COST = "cost"

    OPTIMIZATION = "optimization"

    RECOMMENDATION = "recommendation"

    # ---------------------------------------------------------
    # Migration
    # ---------------------------------------------------------

    MIGRATION = "migration"

    TERRAFORM = "terraform"

    # ---------------------------------------------------------
    # Automation
    # ---------------------------------------------------------

    SELF_HEALING = "self_healing"

    AUTOMATION = "automation"

    # ---------------------------------------------------------
    # Documentation
    # ---------------------------------------------------------

    DOCUMENTATION = "documentation"

    ARCHITECTURE = "architecture"

    # ---------------------------------------------------------
    # General
    # ---------------------------------------------------------

    GENERAL = "general"

    UNKNOWN = "unknown"
