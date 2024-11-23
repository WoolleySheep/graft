class EdgeDrawingProperties:
    """Properties for drawing a networkx edge."""

    def __init__(self, colour: str | None, connection_style: str | None) -> None:
        self.colour = colour
        self.connection_style = connection_style
