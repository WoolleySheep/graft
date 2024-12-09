from collections.abc import Hashable, Sequence
from typing import Protocol

from graft import graphs
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
)


class GetNodePositionsFn[T: Hashable](Protocol):
    def __call__(
        self,
        graph: graphs.DirectedAcyclicGraph[T | DummyNode],
        ordered_layers: Sequence[Sequence[T | DummyNode]],
    ) -> dict[T | DummyNode, tuple[float, float]]: ...
