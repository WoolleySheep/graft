from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import BLACK, Colour


class GraphNodeDrawingProperties:
    """Properties for drawing a networkx node."""

    def __init__(
        self,
        colour: Colour,
        alpha: Alpha = OPAQUE,
        label_colour: Colour = BLACK,
        edge_colour: Colour | None = None,
    ) -> None:
        self._colour = colour
        self._alpha = alpha
        self._edge_colour = edge_colour if edge_colour is not None else colour
        self._label_colour = label_colour

    @property
    def colour(self) -> Colour:
        return self._colour

    @property
    def alpha(self) -> Alpha:
        return self._alpha

    @property
    def edge_colour(self) -> Colour:
        return self._edge_colour

    @property
    def label_colour(self) -> Colour:
        return self._label_colour
