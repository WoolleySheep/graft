from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import Colour


class TaskDrawingProperties:
    """Properties for drawing a network task."""

    def __init__(
        self,
        colour: Colour,
        label_colour: Colour,
        edge_colour: Colour | None = None,
        alpha: Alpha = OPAQUE,
        label_alpha: Alpha = OPAQUE,
    ) -> None:
        self._colour = colour
        self._label_colour = label_colour
        self._edge_colour = edge_colour if edge_colour is not None else colour
        self._alpha = alpha
        self._label_alpha = label_alpha

    @property
    def colour(self) -> Colour:
        return self._colour

    @property
    def label_colour(self) -> Colour:
        return self._label_colour

    @property
    def edge_colour(self) -> Colour:
        return self._edge_colour

    @property
    def alpha(self) -> Alpha:
        return self._alpha

    @property
    def label_alpha(self) -> Alpha:
        return self._label_alpha
