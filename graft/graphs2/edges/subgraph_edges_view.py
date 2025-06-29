from collections.abc import Callable, Hashable, Iterable, Iterator

from ..directed_graph import IDirectedGraphView, SubgraphDirection


class SubgraphEdgesView[T: Hashable]:
    """Abstract view of a collection of unique edges of a subgraph."""

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
        """Check if there are any edges in the collection."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return number of edges in the collection."""
        raise NotImplementedError

    def __contains__(self, edge: tuple[T, T]) -> bool:
        """Check if edge is in the collection."""
        raise NotImplementedError

    def __iter__(self) -> Iterator[tuple[T, T]]:
        """Return iterator over the edges."""
        raise NotImplementedError
