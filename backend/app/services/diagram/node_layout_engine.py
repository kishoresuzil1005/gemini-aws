class NodeLayoutEngine:
    """
    Computes the visual layout of a resource node.
    """

    ICON_SIZE = 48

    ICON_TOP_PADDING = 10

    LABEL_GAP = 10

    PRIMARY_FONT = 13

    SECONDARY_FONT = 10

    @classmethod
    def build(cls, node):

        width = node["width"]

        icon_x = node["x"] + (width - cls.ICON_SIZE) / 2

        icon_y = node["y"] + cls.ICON_TOP_PADDING

        title_y = icon_y + cls.ICON_SIZE + cls.LABEL_GAP

        subtitle_y = title_y + 16

        return {

            "icon_x": icon_x,

            "icon_y": icon_y,

            "title_x": node["x"] + width / 2,

            "title_y": title_y,

            "subtitle_x": node["x"] + width / 2,

            "subtitle_y": subtitle_y

        }
