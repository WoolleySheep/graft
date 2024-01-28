import copy
import itertools
import statistics
from collections.abc import Callable, Collection, Iterable, MutableSequence, Sequence

from graft import graphs
from graft.tkinter_gui.layered_graph_drawing.layer_ordering.utils import (
    calculate_nintersecting_edges_between_layers,
    get_edges_between_layers,
)

NITERATIONS = 30


def _get_initial_layer_orders[T](layers: Sequence[Collection[T]]) -> list[list[T]]:
    return [list(layer) for layer in layers]


def _calc_median_idx_of_neighbours[T](
    node: T,
    neighbours_layer: Sequence[T],
    get_neighbours_fn: Callable[[T], Iterable[T]],
) -> float:
    neighbour_idxs = (
        neighbours_layer.index(neighbour) for neighbour in get_neighbours_fn(node)
    )
    return statistics.median(neighbour_idxs)


def calc_median_idx_of_predecesors[T](
    node: T,
    predecessors_layer: Sequence[T],
    graph: graphs.DirectedAcyclicGraph[T],
) -> float:
    """Get median index of predecessors."""
    return _calc_median_idx_of_neighbours(
        node=node,
        neighbours_layer=predecessors_layer,
        get_neighbours_fn=graph.predecessors,
    )


def calc_median_idx_of_successors[T](
    node: T,
    successors_layer: Sequence[T],
    graph: graphs.DirectedAcyclicGraph[T],
) -> float:
    """Get median index of successors, rounding down."""
    return _calc_median_idx_of_neighbours(
        node=node, neighbours_layer=successors_layer, get_neighbours_fn=graph.successors
    )


def _get_nintersecting_edges_with_adjacent_layers[T](
    layer_idx: int,
    layers: Sequence[MutableSequence[T]],
    graph: graphs.DirectedAcyclicGraph[T],
) -> int:
    nintersecting_edges = 0
    if layer_idx - 1 >= 0:
        previous_layer = layers[layer_idx - 1]
        edges = get_edges_between_layers(
            graph=graph, source_layer=previous_layer, target_layer=layers[layer_idx]
        )
        nintersecting_edges += calculate_nintersecting_edges_between_layers(
            source_layer=previous_layer, target_layer=layers[layer_idx], edges=edges
        )
    if layer_idx + 1 < len(layers):
        next_layer = layers[layer_idx + 1]
        edges = get_edges_between_layers(
            graph=graph, source_layer=layers[layer_idx], target_layer=next_layer
        )
        nintersecting_edges += calculate_nintersecting_edges_between_layers(
            source_layer=layers[layer_idx], target_layer=next_layer, edges=edges
        )
    return nintersecting_edges


def _transpose[T](
    layers: Sequence[MutableSequence[T]], graph: graphs.DirectedAcyclicGraph[T]
) -> None:
    is_improved = True
    while is_improved:
        is_improved = False
        for layer_idx in range(len(layers)):
            layer = layers[layer_idx]

            nintersecting_edges = _get_nintersecting_edges_with_adjacent_layers(
                layer_idx=layer_idx, layers=layers, graph=graph
            )

            for idx1, idx2 in itertools.pairwise(range(len(layer))):
                layers_copy = list(layers)
                layer_copy = copy.copy(layer)
                layer_copy[idx1], layer_copy[idx2] = layer_copy[idx2], layer_copy[idx1]
                layers_copy[layer_idx] = layer_copy

                nintersecting_edges_when_nodes_transposed = (
                    _get_nintersecting_edges_with_adjacent_layers(
                        layer_idx=layer_idx, layers=layers_copy, graph=graph
                    )
                )

                if nintersecting_edges_when_nodes_transposed >= nintersecting_edges:
                    continue

                layer[idx1], layer[idx2] = layer[idx2], layer[idx1]
                nintersecting_edges = nintersecting_edges_when_nodes_transposed

                is_improved = True


def get_layer_orders_median_with_transpose_method[T](
    graph: graphs.DirectedAcyclicGraph[T],
    layers: Sequence[Collection[T]],
) -> list[list[T]]:
    if len(layers) == 0:
        return []

    best_layer_orders = _get_initial_layer_orders(layers=layers)

    for _ in range(NITERATIONS):
        layer_orders = [list(best_layer_orders[0])]
        for layer in itertools.islice(best_layer_orders, 1, None):
            node_median_idx_of_predecessors_map = {
                node: calc_median_idx_of_predecesors(
                    node=node, predecessors_layer=layer_orders[-1], graph=graph
                )
                for node in layer
            }
            sorted_layer = sorted(
                layer, key=lambda node: node_median_idx_of_predecessors_map[node]
            )
            layer_orders.append(sorted_layer)
        best_layer_orders = layer_orders

        layer_orders_reversed = [list(best_layer_orders[-1])]
        for layer in itertools.islice(reversed(best_layer_orders), 1, None):
            node_median_idx_of_successors_map = dict[T, float]()
            for idx, node in enumerate(layer):
                if not graph.successors(node):
                    node_median_idx_of_successors_map[node] = idx
                    continue
                node_median_idx_of_successors_map[node] = calc_median_idx_of_successors(
                    node=node, successors_layer=layer_orders_reversed[-1], graph=graph
                )
            sorted_layer = sorted(
                layer, key=lambda node: node_median_idx_of_successors_map[node]
            )
            layer_orders_reversed.append(sorted_layer)
        best_layer_orders = list(reversed(layer_orders_reversed))

        _transpose(layers=best_layer_orders, graph=graph)

    return best_layer_orders
