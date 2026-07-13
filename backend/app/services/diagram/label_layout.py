class LabelLayout:

    TITLE_OFFSET = 84
    META_OFFSET = 102

    @classmethod
    def compute(cls, node):

        cx = node["x"] + node["width"] / 2

        return {
            "title_x": cx,
            "title_y": node["y"] + cls.TITLE_OFFSET,
            "meta_x": cx,
            "meta_y": node["y"] + cls.META_OFFSET,
        