class HierarchyRules:
    """
    Converts topology relationships into hierarchy parent/child
    relationships used ONLY for layout.

    Only containment relationships should influence hierarchy.

    All association relationships are rendered as edges only.
    """

    #
    # Relationships that create hierarchy
    #
    HIERARCHY_RELATIONSHIPS = {
        "IN_VPC",
        "IN_SUBNET",
        "IN_AZ",
        "MEMBER_OF",
        "CONTAINS",
    }

    #
    # Relationships that DO NOT create hierarchy
    #
    ASSOCIATION_RELATIONSHIPS = {
        "USES_ROLE",
        "USES_SECURITY_GROUP",
        "ATTACHED_VOLUME",
        "ATTACHED_TO",
        "CONNECTS_TO",
        "PEERS_WITH",
        "ROUTES_TO",
        "TARGETS",
        "MOUNTS",
    }

    def resolve(self, edge):

        relation = edge["relationship"]

        source = edge["source"]
        target = edge["target"]

        #
        # Containment hierarchy
        #
        if relation == "IN_VPC":
            return target, source

        if relation == "IN_SUBNET":
            return target, source

        if relation == "IN_AZ":
            return target, source

        if relation == "MEMBER_OF":
            return target, source

        if relation == "CONTAINS":
            return source, target

        #
        # Associations should NOT affect hierarchy
        #
        if relation in self.ASSOCIATION_RELATIONSHIPS:
            return None, None

        #
        # Unknown relationships do not affect hierarchy
        #
        return None, Non