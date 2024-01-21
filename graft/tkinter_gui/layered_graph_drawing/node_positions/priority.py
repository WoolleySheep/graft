import itertools
from collections.abc import Collection, Mapping, MutableMapping, Sequence
from typing import Callable

from graft import graphs
from graft.domain import tasks
from graft.tkinter_gui.layered_graph_drawing.dummy_node import DummyNode

MIN_NODE_SEPARATION_X_DISTANCE = 1


class Priority:
    """Priority of a node for movement purposes.

    Nodes with higher priority can shift nodes with lower. Having no priority
    set is the highest priority of all.
    """

    def __init__(self, n: int | None = None) -> None:
        self.n = n

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise NotImplementedError

        if other.n is None:
            return True

        if self.n is None:
            return False

        return self.n < other.n


def _get_node_starting_x_positions[T](
    ordered_layers: Sequence[Sequence[T]],
    starting_seperation_ratio: float,
) -> dict[T, float]:
    if starting_seperation_ratio < 1:
        raise ValueError

    node_positions = dict[T, float]()
    for layer in ordered_layers:
        for idx, node in enumerate(layer):
            position = (starting_seperation_ratio * MIN_NODE_SEPARATION_X_DISTANCE) * (
                idx - (len(layer) / 2)
            )
            node_positions[node] = position

    return node_positions


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
) -> None:
    if node == tasks.UID(10):
        pass
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
            threshold_position=threshold_position - MIN_NODE_SEPARATION_X_DISTANCE,
            x_positions=x_positions,
            priorities=priorities,
            layer=layer,
        )

    x_positions[node] = max(
        threshold_position, x_positions[leftward_node] + MIN_NODE_SEPARATION_X_DISTANCE
    )


def _shift_nodes_right[T](
    node: T,
    threshold_position: float,
    x_positions: MutableMapping[T, float],
    priorities: Mapping[T, Priority],
    layer: Sequence[T],
) -> None:
    if node == tasks.UID(10):
        pass
    # Node is the leftmost node - base case
    if layer.index(node) == len(layer) - 1:
        if x_positions[node] >= threshold_position:
            return
        x_positions[node] = threshold_position
        return

    rightward_node = layer[layer.index(node) + 1]

    if priorities[rightward_node] < priorities[node]:
        _shift_nodes_right(
            node=rightward_node,
            threshold_position=threshold_position + MIN_NODE_SEPARATION_X_DISTANCE,
            x_positions=x_positions,
            priorities=priorities,
            layer=layer,
        )

    x_positions[node] = min(
        threshold_position, x_positions[rightward_node] - MIN_NODE_SEPARATION_X_DISTANCE
    )


def _move_node[T](
    node: T,
    ideal_position: float,
    layer: Sequence[T],
    node_x_positions: MutableMapping[T, float],
    priorities: Mapping[T, Priority],
) -> None:
    current_position = node_x_positions[node]

    if current_position < ideal_position:
        _shift_nodes_right(
            node=node,
            threshold_position=ideal_position,
            x_positions=node_x_positions,
            priorities=priorities,
            layer=layer,
        )
    elif current_position > ideal_position:
        _shift_nodes_left(
            node=node,
            threshold_position=ideal_position,
            x_positions=node_x_positions,
            priorities=priorities,
            layer=layer,
        )


def _get_node_x_positions[T](
    graph: graphs.DirectedAcyclicGraph[T | DummyNode],
    ordered_layers: Sequence[Sequence[T | DummyNode]],
) -> dict[T | DummyNode, float]:
    starting_separation_ratio = 3
    node_x_positions = _get_node_starting_x_positions(
        ordered_layers=ordered_layers,
        starting_seperation_ratio=starting_separation_ratio,
    )

    forward_priorities = {
        node: _get_forward_priority(node=node, graph=graph) for node in node_x_positions
    }

    backward_priorities = {
        node: _get_backward_priority(node=node, graph=graph)
        for node in node_x_positions
    }

    for _ in range(20):
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
                )

    return node_x_positions


def _get_max_layer_width[T](
    layers: Collection[Collection[T]], x_positions: Mapping[T, float]
) -> float:
    max_layer_width = 0
    for layer in layers:
        max_layer_value = max(x_positions[node] for node in layer)
        min_layer_value = min(x_positions[node] for node in layer)
        layer_width = max_layer_value - min_layer_value
        if layer_width > max_layer_width:
            max_layer_width = layer_width

    return max_layer_width


def _get_node_y_positions[T](
    ordered_layers: Sequence[Sequence[T]], max_layer_width: float
) -> dict[T, float]:
    node_y_positions = dict[T, float]()
    for idx, layer in enumerate(ordered_layers):
        layer_y_pos = -idx * max_layer_width / (len(ordered_layers) - 1)
        for node in layer:
            node_y_positions[node] = layer_y_pos

    return node_y_positions


def _merge_node_positions[T](
    layers: Collection[Collection[T]],
    node_x_positions: Mapping[T, float],
    node_y_positions: Mapping[T, float],
) -> dict[T, tuple[float, float]]:
    node_positions = dict[T, tuple[float, float]]()
    for node in itertools.chain(*layers):
        node_positions[node] = (node_x_positions[node], node_y_positions[node])

    return node_positions


def get_node_positions_vertical_priority_method[T](
    graph: graphs.DirectedAcyclicGraph[T | DummyNode],
    ordered_layers: Sequence[Sequence[T | DummyNode]],
) -> dict[T | DummyNode, tuple[float, float]]:
    """Get node positions using the priority method.

    https://publications.lib.chalmers.se/records/fulltext/161388.pdf
    """

    node_x_positions = _get_node_x_positions(
        graph=graph,
        ordered_layers=ordered_layers,
    )
    node_y_positions = _get_node_y_positions(
        ordered_layers=ordered_layers,
        max_layer_width=_get_max_layer_width(
            layers=ordered_layers, x_positions=node_x_positions
        ),
    )

    return _merge_node_positions(
        layers=ordered_layers,
        node_x_positions=node_x_positions,
        node_y_positions=node_y_positions,
    )
