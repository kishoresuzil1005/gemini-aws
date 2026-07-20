"""Shared constants for the AI Context Engine.

Feature‑flag environment variable names follow the ``<PROVIDER_NAME>_PROVIDER_ENABLED``
convention and default to ``"true"`` if the variable is not set.
"""

# ─────────────────────────────────────────────
#  Feature‑flag env‑variable names
# ─────────────────────────────────────────────
RESOURCE_PROVIDER_ENABLED      = "RESOURCE_PROVIDER_ENABLED"
GRAPH_PROVIDER_ENABLED          = "GRAPH_PROVIDER_ENABLED"
INVENTORY_PROVIDER_ENABLED      = "INVENTORY_PROVIDER_ENABLED"
METRICS_PROVIDER_ENABLED        = "METRICS_PROVIDER_ENABLED"
COST_PROVIDER_ENABLED           = "COST_PROVIDER_ENABLED"
DOCUMENTATION_PROVIDER_ENABLED  = "DOCUMENTATION_PROVIDER_ENABLED"
IAM_PROVIDER_ENABLED            = "IAM_PROVIDER_ENABLED"
CLOUDTRAIL_PROVIDER_ENABLED     = "CLOUDTRAIL_PROVIDER_ENABLED"
EVENTBRIDGE_PROVIDER_ENABLED    = "EVENTBRIDGE_PROVIDER_ENABLED"
CONFIG_PROVIDER_ENABLED         = "CONFIG_PROVIDER_ENABLED"
HEALTH_PROVIDER_ENABLED         = "HEALTH_PROVIDER_ENABLED"
QDRANT_PROVIDER_ENABLED         = "QDRANT_PROVIDER_ENABLED"

# ─────────────────────────────────────────────
#  Engine metadata
# ─────────────────────────────────────────────
ENGINE_VERSION    = "1.0.0"
SCHEMA_VERSION    = "1.0"

# ─────────────────────────────────────────────
#  Default timing
# ─────────────────────────────────────────────
DEFAULT_METRICS_LOOK_BACK_HOURS  = 24
DEFAULT_COST_GRANULARITY         = "daily"
DEFAULT_PROVIDER_TIMEOUT         = 5

# ─────────────────────────────────────────────
#  Default TTLs (seconds)
# ─────────────────────────────────────────────
TTL_STATIC   = 1800   # 30 minutes  – graph, inventory, resource, IAM, documentation
TTL_DYNAMIC  = 120    # 2 minutes   – metrics, cost, events
