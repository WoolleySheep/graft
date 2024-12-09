import itertools
from collections.abc import Container, Generator, Iterable, Sequence

from graft import graphs


def get_edges_between_layers[T](
    graph: graphs.DirectedAcyclicGraph[T],
    source_layer: Container[T],
    target_layer: Container[T],
) -> Generator[tuple[T, T], None, None]:
    """Get the edges from the source to the target layer."""
    for source, target in graph.edges():
        if source in source_layer and target in target_layer:
            yield (source, target)


def _do_edges_intersect(
    edge1_idxs: tuple[int, int],
    edge2_idxs: tuple[int, int],
) -> bool:
    edge1_source_idx = edge1_idxs[0]
    edge1_target_idx = edge1_idxs[1]
    edge2_source_idx = edge2_idxs[0]
    edge2_target_idx = edge2_idxs[1]

    return (
        edge1_source_idx < edge2_source_idx and edge1_target_idx > edge2_target_idx
    ) or (edge1_source_idx > edge2_source_idx and edge1_target_idx < edge2_target_idx)


def calculate_nintersecting_edges_between_layers[T](
    source_layer: Sequence[T],
    target_layer: Sequence[T],
    edges: Iterable[tuple[T, T]],
) -> int:
    """Calculate the number of edges that intersect between the two groups.

    The order of each node in its group corresponds to its index.
    """
    source_uid_idx_map = {uid: idx for idx, uid in enumerate(source_layer)}
    target_uid_idx_map = {uid: idx for idx, uid in enumerate(target_layer)}

    edges_as_idxs = (
        (source_uid_idx_map[source], target_uid_idx_map[target])
        for source, target in edges
    )

    nintersecting_edges = 0
    for edge1, edge2 in itertools.combinations(edges_as_idxs, 2):
        if _do_edges_intersect(edge1, edge2):
            nintersecting_edges += 1

    return nintersecting_edges
