from app.services.diagram.aws_icon_mapper import AWSIconMapper


class LayoutEngine:

    #
    # Canvas
    #
    CANVAS_WIDTH = 1800
    CANVAS_HEIGHT = 1200

    #
    # Layer Size
    #
    LAYER_WIDTH = 1600
    LAYER_HEIGHT = 150

    #
    # Resource Size
    #
    NODE_WIDTH = 90
    NODE_HEIGHT = 90

    #
    # Margins
    #
    START_X = 120
    START_Y = 60

    HORIZONTAL_GAP = 170
    VERTICAL_GAP = 170

    #
    # Layer order
    #
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

        self.mapper = AWSIconMapper()

    def build(self):

        architecture = self.mapper.build()

        layout = {

            "canvas": {

                "width": self.CANVAS_WIDTH,

                "height": self.CANVAS_HEIGHT

            },

            "layers": [],

            "edges": architecture["edges"]

        }

        current_y = self.START_Y

        for layer_name in self.LAYER_ORDER:

            resources = architecture["layers"].get(layer_name, [])

            if not resources:
                continue

            layer = {

                "name": layer_name,

                "x": 60,

                "y": current_y,

                "width": self.LAYER_WIDTH,

                "height": self.LAYER_HEIGHT,

                "resources": []

            }

            current_x = self.START_X

            for resource in resources:

                node = resource.copy()

                node["x"] = current_x
                node["y"] = current_y + 35

                node["width"] = self.NODE_WIDTH
                node["height"] = self.NODE_HEIGHT

                layer["resources"].append(node)

                current_x += self.HORIZONTAL_GAP

            layout["layers"].append(layer)

            current_y += self.VERTICAL_GAP

        return layout
