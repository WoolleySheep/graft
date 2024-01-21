import copy
import itertools
from collections.abc import (
    Callable,
    Collection,
    Container,
    Hashable,
    Mapping,
    MutableMapping,
    Sequence,
    Set,
)
from typing import Iterable, Protocol

import networkx as nx

import graft
from graft import graphs
from graft.domain import tasks
from graft.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
    substitute_dummy_nodes_and_edges,
)
from graft.tkinter_gui.layered_graph_drawing.layer_assignment import (
    GetLayersFn,
    get_layers_topological_grouping_method,
)
from graft.tkinter_gui.layered_graph_drawing.layer_ordering import (
    GetLayerOrdersFn,
    get_layer_orders_brute_force_method,
    get_layer_orders_median_with_transpose_method,
)
from graft.tkinter_gui.layered_graph_drawing.node_positions import (
    GetNodePositionsFn,
    get_node_positions_vertical_priority_method,
)


class CalculateNodePositionsFn(Protocol):
    def __call__[T: Hashable](
        self, graph: graphs.DirectedAcyclicGraph[T]
    ) -> dict[T, tuple[float, float]]:
        ...


def _remove_dummy_nodes[T: Hashable, V](
    node_positions: MutableMapping[T | DummyNode, V],
) -> dict[T, V]:
    return {
        node: value
        for node, value in node_positions.items()
        if not isinstance(node, DummyNode)
    }


def _calculate_node_positions[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
    get_layers_fn: GetLayersFn,
    get_layer_orders_fn: GetLayerOrdersFn,
    get_node_positions_fn: GetNodePositionsFn,
) -> dict[T, tuple[float, float]]:
    layers = get_layers_fn(graph=graph)

    (
        graph_with_dummies,
        layers_with_dummies,
    ) = substitute_dummy_nodes_and_edges(graph=graph, layers=layers)

    layer_orders_with_dummies = get_layer_orders_fn(
        graph=graph_with_dummies, layers=layers_with_dummies
    )

    node_positions = get_node_positions_fn(
        graph=graph_with_dummies, ordered_layers=layer_orders_with_dummies
    )

    return _remove_dummy_nodes(node_positions=node_positions)


def calculate_vertical_node_positions_sugiyama_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> dict[T, tuple[float, float]]:
    return _calculate_node_positions(
        graph=graph,
        get_layers_fn=get_layers_topological_grouping_method,
        get_layer_orders_fn=get_layer_orders_median_with_transpose_method,
        get_node_positions_fn=get_node_positions_vertical_priority_method,
    )


def calculate_vertical_node_positions_brute_force_method[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> dict[T, tuple[float, float]]:
    return _calculate_node_positions(
        graph=graph,
        get_layers_fn=get_layers_topological_grouping_method,
        get_layer_orders_fn=get_layer_orders_brute_force_method,
        get_node_positions_fn=get_node_positions_vertical_priority_method,
    )
