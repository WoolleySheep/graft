from __future__ import annotations

from collections.abc import Callable, Hashable, Iterator
from typing import Iterable

from subgraph_direction import SubgraphDirection

from graft.graphs2.directed_graph import DirectedGraph
from graft.graphs2.directed_graph.cached_graph_view import CachedDirectedGraphView
from graft.graphs2.directed_graph.graph_view_protocol import IDirectedGraphView
from graft.graphs2.nodes.subgraph_neighbour_nodes_view import SubgraphNeighbourNodesView

from ..edges import SubgraphEdgesView
from ..nodes import SubgraphNodesView


class DirectedSubgraphView[T: Hashable]:
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
        """Check if digraph is not empty."""
        raise NotImplementedError

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        raise NotImplementedError

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        raise NotImplementedError

    def degree(self, node: T, /) -> int:
        """Return number of edges to and from node."""
        raise NotImplementedError

    def nodes(self) -> SubgraphNodesView[T]:
        """Return view of nodes in the digraph."""
        raise NotImplementedError

    def edges(self) -> SubgraphEdgesView[T]:
        """Return view of digraph edges."""
        raise NotImplementedError

    def successors(self, node: T, /) -> SubgraphNeighbourNodesView[T]:
        """Return successors of node."""
        raise NotImplementedError

    def predecessors(self, node: T, /) -> SubgraphNeighbourNodesView[T]:
        """Return predecessors of node."""
        raise NotImplementedError

    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the descendants of nodes."""
        raise NotImplementedError

    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the ancestors of nodes."""
        raise NotImplementedError

    def connecting_subgraph(
        self, source_nodes: Iterable[T], target_nodes: Iterable[T]
    ) -> DirectedSubgraphView[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        raise NotImplementedError

    def component(self, node: T) -> DirectedSubgraphView[T]:
        """Return component containing node."""
        raise NotImplementedError

    def components(self) -> Iterator[DirectedSubgraphView[T]]:
        """Yield components in the graph."""
        raise NotImplementedError

    def is_root(self, node: T, /) -> bool:
        """Check if node is a root of the graph."""
        raise NotImplementedError

    def roots(self) -> Iterator[T]:
        """Yield all roots of the graph."""
        raise NotImplementedError

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        raise NotImplementedError

    def leaves(self) -> Iterator[T]:
        """Yield all leaves of the graph."""
        raise NotImplementedError

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        raise NotImplementedError

    def isolated_nodes(self) -> Iterator[T]:
        """Yield all isolated nodes."""
        raise NotImplementedError

    def has_loop(self) -> bool:
        """Check if the graph has a loop."""
        raise NotImplementedError

    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""
        raise NotImplementedError

    def reify(self) -> DirectedGraph[T]:
        """Create a graph equivalent to the view."""
        raise NotImplementedError

    def cache(self) -> CachedDirectedGraphView[T]:
        """Create a cached view of the graph."""
        raise NotImplementedError

    def tee(self, n: int = 2) -> tuple[DirectedSubgraphView[T], ...]:
        """Return a tuple of n independent graph views."""
        raise NotImplementedError
