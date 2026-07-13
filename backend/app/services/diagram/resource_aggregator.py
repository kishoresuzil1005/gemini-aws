from collections import defaultdict

from app.services.diagram.graph_parser import GraphParser


class ResourceAggregator:
    """
    Aggregates discovered AWS resources into logical groups.

    Example:
        EC2 (7)
        Lambda (5)
        VPC (22)
        IAM (13)

    Each aggregated node keeps references to the original resources.
    """

    def __init__(self):
        self.graph_parser = GraphParser()

    def build(self):

        graph = self.graph_parser.parse()

        grouped = defaultdict(list)

        #
        # Group by resource type
        #
        for node in graph["nodes"]:
            grouped[node["type"]].append(node)

        aggregated_resources = []

        for resource_type, resources in grouped.items():

            aggregated_resources.append({

                "id": resource_type,

                "type": resource_type,

                "display_name": f"{resource_type} ({len(resources)})",

                "count": len(resources),

                "children": resources,

                "resource_ids": [
                    r["id"]
                    for r in resources
                ]
            })

        #
        # Sort by count (largest first)
        #
        aggregated_resources.sort(
            key=lambda r: r["count"],
            reverse=True
        )

        return {

            "resources": aggregated_resources,

            "edges": graph["edges"]

        }