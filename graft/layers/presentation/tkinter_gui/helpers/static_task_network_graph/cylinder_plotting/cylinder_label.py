import dataclasses

from graft.layers.presentation.tkinter_gui.helpers.alpha import OPAQUE, Alpha
from graft.layers.presentation.tkinter_gui.helpers.colour import Colour


@dataclasses.dataclass(frozen=True)
class CylinderLabelDrawingProperties:
    colour: Colour
    alpha: Alpha = OPAQUE


@dataclasses.dataclass(frozen=True)
class CylinderLabel:
    text: str
    properties: CylinderLabelDrawingProperties
