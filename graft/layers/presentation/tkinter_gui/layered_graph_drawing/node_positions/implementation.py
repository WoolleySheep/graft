from collections.abc import Hashable, Sequence

from graft import graphs
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.node_positions import (
    inter_layer,
    intra_layer,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.node_positions.components import (
    get_node_positions_inter_component_adjustment,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.node_positions.utils import (
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

    intra_level_positions_component_adjusted = (
        get_node_positions_inter_component_adjustment(
            graph=graph, node_positions=intra_level_positions
        )
    )

    layer_positions = inter_layer.get_layer_positions_max_width_fractions_method(
        intra_layer_positions=intra_level_positions_component_adjusted,
        ordered_layers=ordered_layers,
    )

    return combine_node_positions(
        ordered_layers=ordered_layers,
        intra_layer_positions=intra_level_positions_component_adjusted,
        layer_positions=layer_positions,
    )
