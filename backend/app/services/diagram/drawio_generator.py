from xml.etree.ElementTree import Element, SubElement, tostring

from app.services.diagram.smart_layout_engine import SmartLayoutEngine


class DrawIOGenerator:
    """
    Generates editable Draw.io (.drawio) XML
    from the architecture layout.
    """

    def __init__(self):
        self.layout = SmartLayoutEngine()

    def generate(self):

        layout = self.layout.build()

        mxfile = Element("mxfile")

        diagram = SubElement(
            mxfile,
            "diagram",
            name="AWS Architecture"
        )

        model = SubElement(diagram, "mxGraphModel")

        root = SubElement(model, "root")

        #
        # Required draw.io cells
        #

        cell0 = SubElement(
            root,
            "mxCell",
            id="0"
        )

        cell1 = SubElement(
            root,
            "mxCell",
            id="1",
            parent="0"
        )

        #
        # Add nodes
        #

        cell_id = 2

        id_map = {}

        for node in layout["nodes"]:

            node_id = str(cell_id)

            id_map[node["type"]] = node_id

            cell = SubElement(

                root,

                "mxCell",

                id=node_id,

                value=node["display_name"],

                vertex="1",

                parent="1",

                style=(
                    "rounded=1;"
                    "whiteSpace=wrap;"
                    "html=1;"
                )
            )

            SubElement(

                cell,

                "mxGeometry",

                x=str(node["x"]),

                y=str(node["y"]),

                width=str(node["width"]),

                height=str(node["height"]),

                as_="geometry"

            )

            cell_id += 1

        #
        # Add edges
        #

        for edge in layout["edges"]:

            if edge["source"] not in id_map:
                continue

            if edge["target"] not in id_map:
                continue

            edge_cell = SubElement(

                root,

                "mxCell",

                id=str(cell_id),

                edge="1",

                parent="1",

                source=id_map[edge["source"]],

                target=id_map[edge["target"]]

            )

            SubElement(

                edge_cell,

                "mxGeometry",

                relative="1",

                as_="geometry"

            )

            cell_id += 1

        return tostring(
            mxfile,
            encoding="unicode"
        