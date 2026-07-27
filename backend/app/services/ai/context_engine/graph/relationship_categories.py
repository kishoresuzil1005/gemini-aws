"""Configuration mapping for relationship categories."""

RELATIONSHIP_CATEGORY = {
    "USES_SG": "Security",
    "USES_ROLE": "Security",
    "ATTACHED_TO": "Storage",
    "MOUNTS": "Storage",
    "IN_SUBNET": "Network",
    "IN_VPC": "Network",
    "ROUTES_TO": "Network",
    "PEERS_WITH": "Network"
}

def get_category(relationship: str) -> str:
    """Return the category for a given relationship, defaulting to Infrastructure."""
    if not relationship:
        return "Infrastructure"
    return RELATIONSHIP_CATEGORY.get(relationship.upper(), "Infrastructure")
