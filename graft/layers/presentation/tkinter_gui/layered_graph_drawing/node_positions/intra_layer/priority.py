import itertools
from collections.abc import Collection, Mapping, MutableMapping, Sequence
from typing import Callable

from graft import graphs
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.dummy_node import (
    DummyNode,
)
from graft.layers.presentation.tkinter_gui.layered_graph_drawing.node_positions.intra_layer.even_spacing_around_zero import (
    get_node_positions_even_spacing_around_zero_method,
)


class Priority:
    """Priority of a node for movement purposes.

    Having no priority set is the highest priority of all.
    """

    def __init__(self, n: int | None = None) -> None:
        self.n = n

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise NotImplementedError

        return self.n is not None and (other.n is None or self.n < other.n)


def _get_npredecessors[T](node: T, graph: graphs.DirectedAcyclicGraph[T]) -> int:
    return len(graph.predecessors(node))


def _get_nsuccessors[T](node: T, graph: graphs.DirectedAcyclicGraph[T]) -> int:
    return len(graph.successors(node))


def _get_forward_priority[T](
    node: T | DummyNode, graph: graphs.DirectedAcyclicGraph[T]
) -> Priority:
    if isinstance(node, DummyNode):
        return Priority()

    return Priority(_get_npredecessors(node=node, graph=graph))


def _get_backward_priority[T](
    node: T | DummyNode, graph: graphs.DirectedAcyclicGraph[T]
) -> Priority:
    if isinstance(node, DummyNode):
        return Priority()

    return Priority(_get_nsuccessors(node=node, graph=graph))


def _calculate_neighbours_avg_position[T](
    node: T,
    node_x_positions: Mapping[T, float],
    get_neighbours_fn: Callable[[T], Collection[T]],
) -> float:
    neighbours = get_neighbours_fn(node)
    return sum(node_x_positions[neighbour] for neighbour in neighbours) / len(
        neighbours
    )


def _shift_nodes_left[T](
    node: T,
    threshold_position: float,
    x_positions: MutableMapping[T, float],
    priorities: Mapping[T, Priority],
    layer: Sequence[T],
    min_node_separation_distance: float,
) -> None:
    # Node is the leftmost node - base case
    if layer.index(node) == 0:
        if x_positions[node] <= threshold_position:
            return
        x_positions[node] = threshold_position
        return

    leftward_node = layer[layer.index(node) - 1]

    if priorities[leftward_node] < priorities[node]:
        _shift_nodes_left(
            node=leftward_node,
            threshold_position=threshold_position - min_node_separation_distance,
            x_positions=x_positions,
            priorities=priorities,
            layer=layer,
            min_node_separation_distance=min_node_separation_distance,
        )

    x_positions[node] = max(
        threshold_position, x_positions[leftward_node] + min_node_separation_distance
    )


def _shift_nodes_right[T](
    node: T,
    threshold_position: float,
    x_positions: MutableMapping[T, float],
    priorities: Mapping[T, Priority],
    layer: Sequence[T],
    min_node_separation_distance: float,
) -> None:
    # Node is the rightmost node - base case
    if layer.index(node) == len(layer) - 1:
        if x_positions[node] >= threshold_position:
            return
        x_positions[node] = threshold_position
        return

    rightward_node = layer[layer.index(node) + 1]

    if priorities[rightward_node] < priorities[node]:
        _shift_nodes_right(
            node=rightward_node,
            threshold_position=threshold_position + min_node_separation_distance,
            x_positions=x_positions,
            priorities=priorities,
            layer=layer,
            min_node_separation_distance=min_node_separation_distance,
        )

    x_positions[node] = min(
        threshold_position, x_positions[rightward_node] - min_node_separation_distance
    )


def _move_node[T](
    node: T,
    ideal_position: float,
    layer: Sequence[T],
    node_x_positions: MutableMapping[T, float],
    priorities: Mapping[T, Priority],
    min_node_separation_distance: float,
) -> None:
    current_position = node_x_positions[node]

    if current_position < ideal_position:
        _shift_nodes_right(
            node=node,
            threshold_position=ideal_position,
            x_positions=node_x_positions,
            priorities=priorities,
            layer=layer,
            min_node_separation_distance=min_node_separation_distance,
        )
    elif current_position > ideal_position:
        _shift_nodes_left(
            node=node,
            threshold_position=ideal_position,
            x_positions=node_x_positions,
            priorities=priorities,
            layer=layer,
            min_node_separation_distance=min_node_separation_distance,
        )


def get_node_positions_priority_method[T](
    graph: graphs.DirectedAcyclicGraph[T | DummyNode],
    ordered_layers: Sequence[Sequence[T | DummyNode]],
    min_node_separation_distance: float,
    starting_separation_ratio: float = 2,
    niterations: int = 20,
) -> dict[T | DummyNode, float]:
    """Get node positions using the priority method.

    https://publications.lib.chalmers.se/records/fulltext/161388.pdf

    This method is designed to be direction-agnostic. This returns the node's
    x-position if the graph is vertical, and its y-position if the graph is
    horizontal.
    """
    if min_node_separation_distance <= 0:
        raise ValueError

    if starting_separation_ratio < 1:
        raise ValueError

    if niterations < 1:
        raise ValueError

    node_x_positions = get_node_positions_even_spacing_around_zero_method(
        ordered_layers=ordered_layers,
        starting_separation_ratio=starting_separation_ratio,
        min_node_separation_distance=min_node_separation_distance,
    )

    forward_priorities = {
        node: _get_forward_priority(node=node, graph=graph) for node in node_x_positions
    }

    backward_priorities = {
        node: _get_backward_priority(node=node, graph=graph)
        for node in node_x_positions
    }

    for _ in range(niterations):
        for layer in itertools.islice(ordered_layers, 1, None):
            for node in sorted(
                layer, key=lambda node: forward_priorities[node], reverse=True
            ):
                predecessors_avg_pos = _calculate_neighbours_avg_position(
                    node=node,
                    node_x_positions=node_x_positions,
                    get_neighbours_fn=graph.predecessors,
                )
                _move_node(
                    node=node,
                    ideal_position=predecessors_avg_pos,
                    layer=layer,
                    node_x_positions=node_x_positions,
                    priorities=forward_priorities,
                    min_node_separation_distance=min_node_separation_distance,
                )

        for layer in itertools.islice(reversed(ordered_layers), 1, None):
            for node in sorted(layer, key=lambda node: backward_priorities[node]):
                # Some nodes will not have successors - no need to move these
                if _get_nsuccessors(node=node, graph=graph) == 0:
                    continue
                successors_avg_pos = _calculate_neighbours_avg_position(
                    node=node,
                    node_x_positions=node_x_positions,
                    get_neighbours_fn=graph.successors,
                )
                _move_node(
                    node=node,
                    ideal_position=successors_avg_pos,
                    layer=layer,
                    node_x_positions=node_x_positions,
                    priorities=backward_priorities,
                    min_node_separation_distance=min_node_separation_distance,
                )

    return node_x_positions
