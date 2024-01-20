from collections.abc import Hashable, Sequence
from typing import Protocol

from graft.tkinter_gui.layered_graph_drawing.dummy_node import DummyNode


class GetNodePositionsFn(Protocol):
    def __call__[T: Hashable](
        self,
        ordered_layers: Sequence[Sequence[T | DummyNode]],
    ) -> dict[T, tuple[float, float]]:
        ...
