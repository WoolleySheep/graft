from typing import Final

from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import Colour

_MIN_NUMBER_OF_POLYGONS_FOR_3D_SHAPE: Final = 3


class CylinderDrawingProperties:
    def __init__(
        self,
        colour: Colour,
        edge_colour: Colour | None = None,
        number_of_polygons: int = 10,
        alpha: Alpha = OPAQUE,
    ) -> None:
        if number_of_polygons < _MIN_NUMBER_OF_POLYGONS_FOR_3D_SHAPE:
            msg = "Number of polygons must be at least 3 to form a closed volume."
            raise ValueError(msg)

        self._colour = colour
        self._edge_colour = edge_colour if edge_colour is not None else colour
        self._number_of_polygons = number_of_polygons
        self._alpha = alpha

    @property
    def colour(self) -> Colour:
        return self._colour

    @property
    def edge_colour(self) -> Colour:
        return self._edge_colour

    @property
    def number_of_polygons(self) -> int:
        return self._number_of_polygons

    @property
    def alpha(self) -> Alpha:
        return self._alpha
