from app.services.diagram.resource_aggregator import ResourceAggregator
from app.services.diagram.layer_builder import LayerBuilder


class ArchitectureModelBuilder:
    """
    Builds a logical architecture model from aggregated AWS resources.
    """

    def __init__(self):
        self.aggregator = ResourceAggregator()
        self.layer_builder = LayerBuilder()

    def build(self):

        aggregated = self.aggregator.build()

        architecture = {

            "layers": {

                "Internet": [],

                "Networking": [],

                "Compute": [],

                "Database": [],

                "Storage": [],

                "Monitoring": [],

                "Security": [],

                "Other": []

            },

            "edges": aggregated["edges"]

        }

        #
        # Place each aggregated resource
        # into its architecture layer
        #

        for resource in aggregated["resources"]:

            layer = self.layer_builder.get_layer(

                resource["type"]

            )

            resource["layer"] = layer

            architecture["layers"][layer].append(resource)

        return architecture
