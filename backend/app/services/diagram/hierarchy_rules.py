class HierarchyRules:
    """
    Converts raw topology relationships into
    hierarchy parent/child relationships.

    Returns:
        parent_id, child_id
    """

    def resolve(self, edge):

        relation = edge["relationship"]

        source = edge["source"]
        target = edge["target"]

        #
        # Containment
        #

        if relation in (
            "IN_VPC",
            "IN_SUBNET",
            "IN_AZ",
        ):

            return target, source

        #
        # Attachments
        #

        if relation in (
            "ATTACHED_VOLUME",
            "USES_SECURITY_GROUP",
            "USES_ROLE",
            "ATTACHED_TO",
        ):

            return source, target

        #
        # Default
        #

        return source, target
