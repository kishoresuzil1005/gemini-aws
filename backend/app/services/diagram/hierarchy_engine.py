from collections import deque


class HierarchyEngine:
    """
    Computes topological depth layers for a generic directional graph.

    Responsibilities
    ----------------
    - Calculate indegrees
    - Execute Kahn's topological sort
    - Assign depth layers to all nodes dynamically
    """

    def assign_layers(self, graph):

        layer = {}

        indegree = {}

        for node in graph["nodes"]:
            indegree[node["id"]] = 0

        for parent, children in graph.get("hierarchy_children", {}).items():
            for child in children:
                if child in indegree:
                    indegree[child] += 1

        queue = deque()

        #
        # roots
        #

        for node in graph["nodes"]:

            if indegree[node["id"]] == 0:

                layer[node["id"]] = 0

                queue.append(node["id"])

        while queue:

            current = queue.popleft()

            current_layer = layer[current]

            for child in graph.get("hierarchy_children", {}).get(current, []):

                if child not in layer:

                    layer[child] = current_layer + 1

                else:

                    layer[child] = max(
                        layer[child],
                        current_layer + 1
                    )

                if child in indegree:
                    indegree[child] -= 1

                    if indegree[child] == 0:

                        queue.append(child)

        #
        # Fallback for cycles or disconnected components
        #
        for node in graph["nodes"]:
            if node["id"] not in layer:
                layer[node["id"]] = 0

        return layer
