from collections.abc import Hashable, Sequence

from graft import graphs
from graft.tkinter_gui.layered_graph_drawing.dummy_node import DummyNode
from graft.tkinter_gui.layered_graph_drawing.node_positions import (
    inter_layer,
    intra_layer,
)
from graft.tkinter_gui.layered_graph_drawing.node_positions.utils import (
    combine_node_positions,
)

INTRA_LAYER_STARTING_SEPARATION_RATIO = 3
INTRA_LAYER_PRIORITY_METHOD_NINTERATIONS = 20


def get_node_positions_best_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T | DummyNode],
    ordered_layers: Sequence[Sequence[T | DummyNode]],
) -> dict[T | DummyNode, tuple[float, float]]:
    intra_level_positions = intra_layer.get_node_positions_priority_method(
        graph=graph,
        ordered_layers=ordered_layers,
        starting_separation_ratio=INTRA_LAYER_STARTING_SEPARATION_RATIO,
        niterations=INTRA_LAYER_PRIORITY_METHOD_NINTERATIONS,
    )
    layer_positions = inter_layer.get_layer_positions_max_width_fractions_method(
        intra_layer_positions=intra_level_positions, ordered_layers=ordered_layers
    )

    return combine_node_positions(
        ordered_layers=ordered_layers,
        intra_layer_positions=intra_level_positions,
        layer_positions=layer_positions,
    )
