from collections.abc import Hashable

from graft import graphs
from graft.tkinter_gui.layered_graph_drawing import layer_ordering, node_positions
from graft.tkinter_gui.layered_graph_drawing.layer_assignment import (
    get_layers_topological_grouping_method,
)
from graft.tkinter_gui.layered_graph_drawing.orientation import GraphOrientation
from graft.tkinter_gui.layered_graph_drawing.template import calculate_node_positions


def calculate_node_positions_sugiyama_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
    orientation: GraphOrientation,
) -> dict[T, tuple[float, float]]:
    return calculate_node_positions(
        graph=graph,
        get_layers_fn=get_layers_topological_grouping_method,
        get_layer_orders_fn=layer_ordering.get_layer_orders_median_with_transpose_method,
        get_node_positions_fn=node_positions.get_node_positions_best_method,
        orientation=orientation,
    )
