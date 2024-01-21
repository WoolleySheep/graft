import itertools
from collections.abc import Callable, Collection, Container, Hashable, Sequence

from graft import graphs


class DummyNode:
    def __init__(self, n: int) -> None:
        self.n = n

    def __hash__(self) -> int:
        return hash(f"dummy{self.n}")

    def __str__(self) -> str:
        return f"DummyNode({self.n})"

    def __repr__(self) -> str:
        return str(self)


def _create_dummy_node_factory() -> Callable[[], DummyNode]:
    """Create a factory that produces new dummy nodes when called."""
    count = 0

    def inner() -> DummyNode:
        nonlocal count
        count += 1
        return DummyNode(n=count)

    return inner


def _copy_graph_to_allow_dummies[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> graphs.DirectedAcyclicGraph[T | DummyNode]:
    """Copy a graph to allow dummy nodes."""
    graph_with_dummies = graphs.DirectedAcyclicGraph[T | DummyNode]()
    for node in graph.nodes():
        graph_with_dummies.add_node(node)
    for source, target in graph.edges():
        graph_with_dummies.add_edge(source, target)
    return graph_with_dummies


def _get_layer_idxs_containing_edge[T](
    source: T, target: T, layers: Sequence[Container[T]]
) -> tuple[int, int]:
    """Get the indexes of the groups containing each end of an edge."""
    groups_iter = iter(layers)
    for idx, group in enumerate(groups_iter):
        if source in group:
            source_idx = idx
            break
    else:
        raise ValueError

    for idx, group in enumerate(groups_iter, source_idx + 1):
        if target in group:
            return source_idx, idx

    raise ValueError


def substitute_dummy_nodes_and_edges[T](
    graph: graphs.DirectedAcyclicGraph[T], layers: Sequence[Collection[T]]
) -> tuple[
    graphs.DirectedAcyclicGraph[T | DummyNode],
    list[set[T | DummyNode]],
]:
    """Replace edges that stretch over 2+ layers with dummy nodes & edges.

    This function does no modify the arguments in place, but returns new copies
    with the dummy nodes & edges substituted.

    Dummy edges only every go from one layer to the next. Add dummy nodes to
    accomodate these edges. The end result should be a graph with edges that
    only every go one layer down.
    """
    graph_with_dummies = _copy_graph_to_allow_dummies(graph=graph)
    layers_with_dummies: list[set[T | DummyNode]] = [set(group) for group in layers]

    dummy_node_factory = _create_dummy_node_factory()

    for source, target in graph.edges():
        source_layer_idx, target_layer_idx = _get_layer_idxs_containing_edge(
            source=source,
            target=target,
            layers=layers,
        )

        if (target_layer_idx - source_layer_idx) == 1:
            continue

        graph_with_dummies.remove_edge(source, target)

        dummy_nodes_to_replace_edge = list[DummyNode]()
        for group_idx in range(source_layer_idx + 1, target_layer_idx):
            dummy_node = dummy_node_factory()

            graph_with_dummies.add_node(dummy_node)

            layers_with_dummies[group_idx].add(dummy_node)
            dummy_nodes_to_replace_edge.append(dummy_node)

        for dummy_source, dummy_target in itertools.pairwise(
            itertools.chain([source], dummy_nodes_to_replace_edge, [target])
        ):
            graph_with_dummies.add_edge(dummy_source, dummy_target)

    return graph_with_dummies, layers_with_dummies
