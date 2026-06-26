class LabelCollisionDetector:

    def __init__(self):

        self._boxes = []

    def allow(self, x, y, width, height):

        for bx, by, bw, bh in self._boxes:

            if (
                x < bx + bw
                and x + width > bx
                and y < by + bh
                and y + height > by
            ):
                return False

        self._boxes.append(
            (x, y, width, height)
        )

        return True
