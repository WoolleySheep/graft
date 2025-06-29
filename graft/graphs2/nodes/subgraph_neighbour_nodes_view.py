from collections.abc import Callable, Hashable, Iterable, Iterator

from neighbour_direction import NeighbourDirection

from graft.graphs2.bidict import BiDirectionalSetDict
from graft.graphs2.directed_graph.graph_view_protocol import IDirectedGraphView
from graft.graphs2.directed_graph.subgraph_direction import SubgraphDirection


class SubgraphNeighbourNodesView[T: Hashable]:
    """View of a collection of predecessor/successor nodes of a node in a subgraph."""

    def __init__(
        self,
        graph: IDirectedGraphView[T],
        subgraph_direction: SubgraphDirection,
        starting_nodes: Iterable[T],
        cache: BiDirectionalSetDict[T],
        neighbour_direction: NeighbourDirection,
        node: T,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        self._graph = graph
        self._subgraph_direction = subgraph_direction
        self._starting_nodes = starting_nodes
        self._cache = cache
        self._neighbour_direction = neighbour_direction
        self._node = node
        self._stop_condition = stop_condition

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
