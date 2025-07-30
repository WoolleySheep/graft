from collections.abc import Hashable, Sequence

from graft import graphs
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.node_positions import (
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
    min_intra_layer_node_seperation: float,
    min_inter_layer_node_seperation: float,
) -> dict[T | DummyNode, tuple[float, float]]:
    if min_intra_layer_node_seperation <= 0:
        raise ValueError

    if min_inter_layer_node_seperation <= 0:
        raise ValueError

    intra_level_positions = intra_layer.get_node_positions_priority_method(
        graph=graph,
        ordered_layers=ordered_layers,
        min_node_separation_distance=min_intra_layer_node_seperation,
        starting_separation_ratio=INTRA_LAYER_STARTING_SEPARATION_RATIO,
        niterations=INTRA_LAYER_PRIORITY_METHOD_NINTERATIONS,
    )

    intra_level_positions_component_adjusted = (
        get_node_positions_inter_component_adjustment(
            graph=graph,
            node_positions=intra_level_positions,
            component_separation_distance=min_intra_layer_node_seperation,
        )
    )

    layer_positions = [
        n * min_inter_layer_node_seperation for n in range(len(ordered_layers))
    ]

    return combine_node_positions(
        ordered_layers=ordered_layers,
        intra_layer_positions=intra_level_positions_component_adjusted,
        layer_positions=layer_positions,
    )
