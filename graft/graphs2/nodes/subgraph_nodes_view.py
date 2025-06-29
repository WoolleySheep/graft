from collections.abc import Callable, Hashable, Iterable, Iterator

from ..directed_graph import IDirectedGraphView, SubgraphDirection


class SubgraphNodesView[T: Hashable]:
    def __init__(
        self,
        graph: IDirectedGraphView[T],
        direction: SubgraphDirection,
        starting_nodes: Iterable[T],
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        self._graph = graph
        self._direction = direction
        self._starting_nodes = starting_nodes
        self._stop_condition = stop_condition

    def __bool__(self) -> bool:
        """Check if there are any nodes in the collection."""
        try:
            next(iter(self))
        except StopIteration:
            return False
        return True

    def __len__(self) -> int:
        """Return number of nodes in the collection."""
        return sum(1 for _ in self)

    def __contains__(self, node: T) -> bool:
        """Check if node is in the collection."""
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """Return iterator over the nodes."""
        raise NotImplementedError
