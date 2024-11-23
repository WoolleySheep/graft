class NodeDrawingProperties:
    """Properties for drawing a networkx node."""

    def __init__(self, colour: str | None, edge_colour: str | None) -> None:
        self.colour = colour
        self.edge_colour = edge_colour
