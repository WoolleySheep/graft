from collections.abc import (
    Hashable,
    Mapping,
)
from typing import Protocol

from graft import graphs
from graft.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
    substitute_dummy_nodes_and_edges,
)
from graft.tkinter_gui.layered_graph_drawing.layer_assignment import (
    GetLayersFn,
)
from graft.tkinter_gui.layered_graph_drawing.layer_ordering import (
    GetLayerOrdersFn,
)
from graft.tkinter_gui.layered_graph_drawing.node_positions import (
    GetNodePositionsFn,
)
from graft.tkinter_gui.layered_graph_drawing.orientation import (
    GraphOrientation,
    get_place_nodes_fn,
)


class CalculateNodePositionsFn(Protocol):
    def __call__[T: Hashable](
        self, graph: graphs.DirectedAcyclicGraph[T]
    ) -> dict[T, tuple[float, float]]:
        ...


def _remove_dummy_nodes[T: Hashable, V](
    node_positions: Mapping[T | DummyNode, V],
) -> dict[T, V]:
    return {
        node: value
        for node, value in node_positions.items()
        if not isinstance(node, DummyNode)
    }


def calculate_node_positions[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
    get_layers_fn: GetLayersFn,
    get_layer_orders_fn: GetLayerOrdersFn,
    get_node_positions_fn: GetNodePositionsFn,
    orientation: GraphOrientation,
) -> dict[T, tuple[float, float]]:
    layers = get_layers_fn(graph=graph)

    (
        graph_with_dummies,
        layers_with_dummies,
    ) = substitute_dummy_nodes_and_edges(graph=graph, layers=layers)

    layer_orders_with_dummies = get_layer_orders_fn(
        graph=graph_with_dummies, layers=layers_with_dummies
    )

    node_positions_with_dummies = get_node_positions_fn(
        graph=graph_with_dummies, ordered_layers=layer_orders_with_dummies
    )

    node_positions = _remove_dummy_nodes(node_positions=node_positions_with_dummies)

    place_nodes_fn = get_place_nodes_fn(orientation=orientation)

    return place_nodes_fn(node_positions=node_positions)
