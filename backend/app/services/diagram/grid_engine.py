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
            row = node.get("row", 0)
            rows_map[row].append(node)

        current_visual_row = 0

        # For each row, sort by X to determine columns
        for row_index in sorted(rows_map.keys()):
            row_nodes = rows_map[row_index]
            row_nodes.sort(key=lambda n: n.get("x", 0))
            
            # Ensure visual row doesn't fall behind logical topological row
            current_visual_row = max(current_visual_row, row_index)
            
            for index, node in enumerate(row_nodes):
                
                visual_row = current_visual_row + (index // self.columns)
                visual_col = index % self.columns
                
                x, y = self.grid_to_canvas(visual_row, visual_col)
                
                node["row"] = visual_row
                node["column"] = visual_col
                
                # Grid owns positioning
                node["x"] = x
                node["y"] = y
                
                positioned.append(node)

            if row_nodes:
                current_visual_row += (len(row_nodes) - 1) // self.columns + 1
            else:
                current_visual_row += 1

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
        