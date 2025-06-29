from collections.abc import Hashable, Iterator

from ..bidict import BiDirectionalSetDict
from ..directed_graph import IDirectedGraphView


class CachedEdgesView[T: Hashable]:
    """Abstract view of a collection of unique edges of a cached graph."""

    def __init__(
        self, graph: IDirectedGraphView[T], cache: BiDirectionalSetDict[T]
    ) -> None:
        self._graph = graph
        self._cache = cache

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
