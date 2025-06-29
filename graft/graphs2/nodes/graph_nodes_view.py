from collections.abc import Hashable, Iterator, Set


class NodesView[T: Hashable]:
    """View of a collection of nodes in a graph."""

    def __init__(self, nodes: Set[T]) -> None:
        self._nodes = nodes

    def __bool__(self) -> bool:
        """Check if there are any nodes in the collection."""
        return bool(self._nodes)

    def __len__(self) -> int:
        """Return number of nodes in the collection."""
        return len(self._nodes)

    def __contains__(self, node: T) -> bool:
        """Check if node is in the collection."""
        return node in self._nodes

    def __iter__(self) -> Iterator[T]:
        """Return iterator over the nodes."""
        return iter(self._nodes)
