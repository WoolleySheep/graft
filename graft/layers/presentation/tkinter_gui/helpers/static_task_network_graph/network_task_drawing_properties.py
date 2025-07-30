from typing import Final

from graft.layers.presentation.tkinter_gui.helpers.alpha import Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import BLACK, Colour

_DEFAULT_NETWORK_TASK_ALPHA: Final = Alpha(0.8)
_DEFAULT_NETWORK_TASK_LABEL_ALPHA: Final = Alpha(0.95)


class NetworkTaskDrawingProperties:
    """Properties for drawing a network task."""

    def __init__(
        self,
        colour: Colour,
        label_colour: Colour = BLACK,
        edge_colour: Colour | None = None,
        alpha: Alpha = _DEFAULT_NETWORK_TASK_ALPHA,
        label_alpha: Alpha = _DEFAULT_NETWORK_TASK_LABEL_ALPHA,
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
