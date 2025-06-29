from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Iterator

from graph_view_protocol import IDirectedGraphView

from graft.graphs2.directed_graph import DirectedGraph
from graft.graphs2.directed_graph.ancestor_descendant_subgraph_view import (
    DirectedSubgraphView,
)
from graft.graphs2.edges.cached_graph_edges_view import CachedEdgesView
from graft.graphs2.nodes.cached_graph_nodes_view import CachedGraphNodesView
from graft.graphs2.nodes.cached_neighbour_nodes_view import CachedNeighbourNodesView

from ..bidict import BiDirectionalSetDict


class CachedDirectedGraphView[T: Hashable]:
    def __init__(self, graph: IDirectedGraphView[T]) -> None:
        self._graph = graph
        self._bidict = BiDirectionalSetDict[T]()

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

    def nodes(self) -> CachedGraphNodesView[T]:
        """Return view of nodes in the digraph."""
        raise NotImplementedError

    def edges(self) -> CachedEdgesView[T]:
        """Return view of digraph edges."""
        raise NotImplementedError

    def successors(self, node: T, /) -> CachedNeighbourNodesView[T]:
        """Return successors of node."""
        raise NotImplementedError

    def predecessors(self, node: T, /) -> CachedNeighbourNodesView[T]:
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

    def tee(self, n: int = 2) -> tuple[CachedDirectedGraphView[T], ...]:
        """Return a tuple of n independent graph views."""
        raise NotImplementedError
