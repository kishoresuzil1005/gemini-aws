from dataclasses import dataclass
from math import ceil


@dataclass(frozen=True)
class GridCell:
    row: int
    column: int
    x: int
    y: int


class GridEngine:
    """
    Generic grid layout engine.

    Responsibilities
    ----------------
    - Snap coordinates to a grid
    - Allocate cells
    - Convert row/column to canvas coordinates
    - Calculate canvas size

    This engine has NO knowledge of AWS resources.
    """

    CELL_WIDTH = 220
    CELL_HEIGHT = 160

    HORIZONTAL_GAP = 40
    VERTICAL_GAP = 50

    LEFT_MARGIN = 80
    TOP_MARGIN = 80

    RIGHT_MARGIN = 80
    BOTTOM_MARGIN = 80

    DEFAULT_COLUMNS = 6

    def __init__(self, columns: int | None = None):

        self.columns = columns or self.DEFAULT_COLUMNS

    # --------------------------------------------------

    def snap(self, value: float, step: int) -> int:

        """
        Snap a coordinate to the nearest grid line.
        """

        return round(value / step) * step

    # --------------------------------------------------

    def grid_to_canvas(
        self,
        row: int,
        column: int,
    ) -> tuple[int, int]:

        x = (
            self.LEFT_MARGIN
            + column * (self.CELL_WIDTH + self.HORIZONTAL_GAP)
        )

        y = (
            self.TOP_MARGIN
            + row * (self.CELL_HEIGHT + self.VERTICAL_GAP)
        )

        return x, y

    # --------------------------------------------------

    def allocate(self, nodes: list[dict]) -> list[dict]:

        """
        Assign grid coordinates to nodes.

        Input:
            list of nodes

        Output:
            same nodes with:
                row
                column
                x
                y
        """

        positioned = []

        for index, node in enumerate(nodes):

            row = index // self.columns

            column = index % self.columns

            x, y = self.grid_to_canvas(
                row,
                column,
            )

            positioned.append({
                **node,
                "row": row,
                "column": column,
                "x": x,
                "y": y,
            })

        return positioned

    # --------------------------------------------------

    def canvas_size(
        self,
        node_count: int,
    ) -> tuple[int, int]:

        rows = max(
            1,
            ceil(node_count / self.columns),
        )

        width = (
            self.LEFT_MARGIN
            + self.RIGHT_MARGIN
            + self.columns * self.CELL_WIDTH
            + (self.columns - 1) * self.HORIZONTAL_GAP
        )

        height = (
            self.TOP_MARGIN
            + self.BOTTOM_MARGIN
            + rows * self.CELL_HEIGHT
            + (rows - 1) * self.VERTICAL_GAP
        )

        return width, height

    # --------------------------------------------------

    def build(
        self,
        nodes: list[dict],
    ) -> dict:

        """
        Build a complete grid layout.
        """

        nodes = self.allocate(nodes)

        width, height = self.canvas_size(
            len(nodes)
        )

        return {
            "nodes": nodes,
            "canvas": {
                "width": width,
                "height": height,
            },
        }
