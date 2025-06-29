from __future__ import annotations

import copy
from collections.abc import Hashable, Iterable, Iterator
from typing import Callable

from cached_graph_view import CachedDirectedGraphView
from directed_graph import DirectedGraph

from graft.graphs2.directed_graph.ancestor_descendant_subgraph_view import (
    DirectedSubgraphView,
)

from ..edges import EdgesView
from ..nodes import NodesView


class DirectedGraphView[T: Hashable]:
    """View of digraph."""

    def __init__(self, graph: DirectedGraph[T]) -> None:
        self._graph = graph

    def __bool__(self) -> bool:
        """Check if digraph is not empty."""
        return bool(self._graph)

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        return self._graph.in_degree(node)

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        return self._graph.out_degree(node)

    def degree(self, node: T, /) -> int:
        """Return number of edges to and from node."""
        return self._graph.degree(node)

    def nodes(self) -> NodesView[T]:
        """Return view of nodes in the digraph."""
        return self._graph.nodes()

    def edges(self) -> EdgesView[T]:
        """Return view of digraph edges."""
        return self._graph.edges()

    def successors(self, node: T, /) -> NodesView[T]:
        """Return successors of node."""
        return self._graph.successors(node)

    def predecessors(self, node: T, /) -> NodesView[T]:
        """Return predecessors of node."""
        return self._graph.predecessors(node)

    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the descendants of nodes."""
        return self._graph.descendants_subgraph(nodes, stop_condition)

    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the ancestors of nodes."""
        return self._graph.ancestors_subgraph(nodes, stop_condition)

    def connecting_subgraph(
        self, source_nodes: Iterable[T], target_nodes: Iterable[T]
    ) -> DirectedSubgraphView[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        return self._graph.connecting_subgraph(source_nodes, target_nodes)

    def component(self, node: T) -> DirectedSubgraphView[T]:
        """Return component containing node."""
        return self._graph.component(node)

    def components(self) -> Iterator[DirectedSubgraphView[T]]:
        """Yield components in the graph."""
        return self._graph.components()

    def is_root(self, node: T, /) -> bool:
        """Check if node is a root of the graph."""
        return self._graph.is_root(node)

    def roots(self) -> Iterator[T]:
        """Yield all roots of the graph."""
        return self._graph.roots()

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        return self._graph.is_leaf(node)

    def leaves(self) -> Iterator[T]:
        """Yield all leaves of the graph."""
        return self._graph.leaves()

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        return self._graph.is_isolated(node)

    def isolated_nodes(self) -> Iterator[T]:
        """Yield all isolated nodes."""
        return self._graph.isolated_nodes()

    def has_loop(self) -> bool:
        """Check if the graph has a loop."""
        return self._graph.has_loop()

    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""
        return self._graph.has_cycle()

    def reify(self) -> DirectedGraph[T]:
        """Create a graph equivalent to the view."""
        return copy.deepcopy(self._graph)

    def cache(self) -> CachedDirectedGraphView[T]:
        """Create a cached view of the graph."""
        return CachedDirectedGraphView(self._graph)

    def tee(self, n: int = 2) -> tuple[DirectedGraphView[T], ...]:
        """Return a tuple of n independent graph views."""
        raise NotImplementedError
