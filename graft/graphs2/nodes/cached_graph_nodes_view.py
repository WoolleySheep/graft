from collections.abc import Hashable, Iterator

from graft.graphs2.bidict import BiDirectionalSetDict
from graft.graphs2.directed_graph.graph_view_protocol import IDirectedGraphView


class CachedGraphNodesView[T: Hashable]:
    """View of a collection of nodes in a cached graph."""

    def __init__(
        self, graph: IDirectedGraphView[T], cache: BiDirectionalSetDict[T]
    ) -> None:
        self._graph = graph
        self._cache = cache

    def __bool__(self) -> bool:
        """Check if there are any nodes in the collection."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return number of nodes in the collection."""
        raise NotImplementedError

    def __contains__(self, node: T) -> bool:
        """Check if node is in the collection."""
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """Return iterator over the nodes."""
        raise NotImplementedError
