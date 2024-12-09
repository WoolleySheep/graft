class TaskDrawingProperties:
    """Properties for drawing a network task."""

    def __init__(
        self,
        colour: str | None = None,
        alpha: float | None = None,
        label_colour: str | None = None,
        label_alpha: float | None = None,
    ) -> None:
        self.colour = colour
        self.alpha = alpha
        self.label_colour = label_colour
        self.label_alpha = label_alpha
