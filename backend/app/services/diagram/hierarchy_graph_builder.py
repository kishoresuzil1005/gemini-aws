from collections import defaultdict


class HierarchyGraphBuilder:
    """
    Interprets AWS relationship semantics and builds a structural hierarchy graph
    dedicated for diagram rendering, independent of functional dependencies.
    """

    def build(self, edges):

        hierarchy_children = defaultdict(list)
        hierarchy_parents = defaultdict(list)

        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            relation = edge["relationship"]

            #
            # Build hierarchy graph based on semantic rules
            #

            if relation == "IN_VPC":

                hierarchy_children[target].append(source)
                hierarchy_parents[source].append(target)

            elif relation == "IN_SUBNET":

                hierarchy_children[target].append(source)
                hierarchy_parents[source].append(target)

            elif relation == "ATTACHED_VOLUME":

                hierarchy_children[source].append(target)
                hierarchy_parents[target].append(source)

            elif relation == "USES_SECURITY_GROUP":

                hierarchy_children[source].append(target)
                hierarchy_parents[target].append(source)

            elif relation == "USES_ROLE":

                hierarchy_children[source].append(target)
                hierarchy_parents[target].append(source)

            else:

                hierarchy_children[source].append(target)
                hierarchy_parents[target].append(source)

        return dict(hierarchy_children), dict(hierarchy_parents)
