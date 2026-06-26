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

        # Group nodes by their existing layer/Y coordinate to determine rows
        from collections import defaultdict
        rows_map = defaultdict(list)
        
        for node in nodes:
            # If layer is available, use it as the row. Otherwise, fallback to an arbitrary row
            row = node.get("layer", 0)
            rows_map[row].append(node)

        # For each row, sort by X to determine columns
        for row_index, row_nodes in rows_map.items():
            row_nodes.sort(key=lambda n: n.get("x", 0))
            
            for col_index, node in enumerate(row_nodes):
                x, y = self.grid_to_canvas(row_index, col_index)
                
                # If SmartLayoutEngine already set a good X, keep it. But we must provide row/col.
                # Actually, AlignmentEngine expects grid_to_canvas output for Y, and maybe X.
                # Let's keep the X from SmartLayoutEngine since it did a spanning tree layout!
                # But we use grid_to_canvas for Y to ensure row alignment.
                
                node["row"] = row_index
                node["column"] = col_index
                
                # We KEEP the node["x"] if it exists, otherwise use grid x
                node["x"] = node.get("x", x)
                node["y"] = y
                
                positioned.append(node)

        return positioned

    # --------------------------------------------------

    def canvas_size(
        self,
        nodes: list[dict],
    ) -> tuple[int, int]:
    
        if not nodes:
            return 800, 600

        max_row = max(n.get("row", 0) for n in nodes)
        max_col = max(n.get("column", 0) for n in nodes)
        
        rows = max_row + 1
        cols = max_col + 1

        width = (
            self.LEFT_MARGIN
            + self.RIGHT_MARGIN
            + cols * self.CELL_WIDTH
            + (cols - 1) * self.HORIZONTAL_GAP
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

        width, height = self.canvas_size(nodes)

        return {
            "nodes": nodes,
            "canvas": {
                "width": width,
                "height": height,
            },
        }
