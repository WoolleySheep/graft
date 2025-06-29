from collections.abc import Hashable, Iterator, Mapping, Set


class EdgesView[T: Hashable]:
    """View of a collection of edges in a graph."""

    def __init__(self, node_successors_map: Mapping[T, Set[T]]) -> None:
        self._node_successors_map = node_successors_map

    def __bool__(self) -> bool:
        """Check if there are any edges in the collection."""
        return any(
            bool(successors) for successors in self._node_successors_map.values()
        )

    def __len__(self) -> int:
        """Return number of edges in the collection."""
        return sum(len(successors) for successors in self._node_successors_map.values())

    def __contains__(self, edge: tuple[T, T]) -> bool:
        """Check if edge is in the collection."""
        source, target = edge
        return (
            source in self._node_successors_map
            and target in self._node_successors_map[source]
        )

    def __iter__(self) -> Iterator[tuple[T, T]]:
        """Return iterator over the edges."""
        for node, successors in self._node_successors_map.items():
            for successor in successors:
                yield node, successor
