from app.services.diagram.architecture_model_builder import (
    ArchitectureModelBuilder
)


class LayoutEngine:
    """
    Computes positions for architecture nodes.

    Responsible ONLY for layout.
    """

    #
    # Layout Constants
    #

    NODE_WIDTH = 180
    NODE_HEIGHT = 80

    HORIZONTAL_SPACING = 70
    VERTICAL_SPACING = 120

    LEFT_MARGIN = 80
    TOP_MARGIN = 80

    LAYER_ORDER = [

        "Internet",

        "Networking",

        "Compute",

        "Database",

        "Storage",

        "Monitoring",

        "Security",

        "Other"

    ]

    def __init__(self):

        self.builder = ArchitectureModelBuilder()

    def build(self):

        architecture = self.builder.build()

        positioned_nodes = []

        max_width = 0

        current_y = self.TOP_MARGIN

        #
        # Layout one layer at a time
        #

        for layer_name in self.LAYER_ORDER:

            resources = architecture["layers"].get(layer_name, [])

            if not resources:
                continue

            current_x = self.LEFT_MARGIN

            for resource in resources:

                resource["x"] = current_x

                resource["y"] = current_y

                resource["width"] = self.NODE_WIDTH

                resource["height"] = self.NODE_HEIGHT

                positioned_nodes.append(resource)

                current_x += (
                    self.NODE_WIDTH
                    + self.HORIZONTAL_SPACING
                )

            max_width = max(max_width, current_x)

            current_y += (
                self.NODE_HEIGHT
                + self.VERTICAL_SPACING
            )

        canvas = {

            "width": max_width + self.LEFT_MARGIN,

            "height": current_y + self.TOP_MARGIN

        }

        return {

            "canvas": canvas,

            "nodes": positioned_nodes,

            "edges": architecture["edges"]

        }