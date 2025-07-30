from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.arrow_style import (
    CURVE_FILLED_B,
    ArrowStyle,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import Colour
from graft.layers.presentation.tkinter_gui.helpers.connection_style import (
    ARC3,
    ConnectionStyle,
)
from graft.layers.presentation.tkinter_gui.helpers.line_style import SOLID, LineStyle


class GraphEdgeDrawingProperties:
    """Properties for drawing a networkx edge."""

    def __init__(
        self,
        colour: Colour,
        alpha: Alpha = OPAQUE,
        line_style: LineStyle = SOLID,
        connection_style: ConnectionStyle = ARC3,
        arrow_style: ArrowStyle = CURVE_FILLED_B,
    ) -> None:
        self._colour = colour
        self._alpha = alpha
        self._line_style = line_style
        self._connection_style = connection_style
        self._arrow_style = arrow_style

    @property
    def colour(self) -> Colour:
        return self._colour

    @property
    def alpha(self) -> Alpha:
        return self._alpha

    @property
    def line_style(self) -> LineStyle:
        return self._line_style

    @property
    def connection_style(self) -> ConnectionStyle:
        return self._connection_style

    @property
    def arrow_style(self) -> ArrowStyle:
        return self._arrow_style
