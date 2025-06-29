from __future__ import annotations

from collections.abc import Hashable, Iterable, Iterator
from typing import Callable, Protocol

from graph import DirectedGraph

from graft.graphs2.directed_graph.ancestor_descendant_subgraph_view import (
    DirectedSubgraphView,
)
from graft.graphs2.directed_graph.cached_graph_view import CachedDirectedGraphView

from ..edges.edges_view_protocol import IEdgesView
from ..nodes.nodes_view_protocol import INodesView


class IDirectedGraphView[T: Hashable](Protocol):
    """Interface to a view of a digraph with no parallel edges."""

    def __bool__(self) -> bool:
        """Check if digraph is not empty."""
        ...

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        ...

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        ...

    def degree(self, node: T, /) -> int:
        """Return number of edges to and from node."""
        ...

    def nodes(self) -> INodesView[T]:
        """Return view of nodes in the digraph."""
        ...

    def edges(self) -> IEdgesView[T]:
        """Return view of digraph edges."""
        ...

    def successors(self, node: T, /) -> INodesView[T]:
        """Return successors of node."""
        ...

    def predecessors(self, node: T, /) -> INodesView[T]:
        """Return predecessors of node."""
        ...

    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the descendants of nodes."""
        ...

    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the ancestors of nodes."""
        ...

    def connecting_subgraph(
        self, source_nodes: Iterable[T], target_nodes: Iterable[T]
    ) -> DirectedSubgraphView[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        ...

    def component(self, node: T) -> DirectedSubgraphView[T]:
        """Return component containing node."""
        ...

    def components(self) -> Iterator[DirectedSubgraphView[T]]:
        """Yield components in the graph."""
        ...

    def is_root(self, node: T, /) -> bool:
        """Check if node is a root of the graph."""
        ...

    def roots(self) -> Iterator[T]:
        """Yield all roots of the graph."""
        ...

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        ...

    def leaves(self) -> Iterator[T]:
        """Yield all leaves of the graph."""
        ...

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        ...

    def isolated_nodes(self) -> Iterator[T]:
        """Yield all isolated nodes."""
        ...

    def has_loop(self) -> bool:
        """Check if the graph has a loop."""
        ...

    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""
        ...

    def reify(self) -> DirectedGraph[T]:
        """Create a graph equivalent to the view."""
        ...

    def cache(self) -> CachedDirectedGraphView[T]:
        """Create a cached view of the graph."""
        ...

    def tee(self, n: int = 2) -> tuple[IDirectedGraphView[T], ...]:
        """Return a tuple of n independent graph views."""
        ...
