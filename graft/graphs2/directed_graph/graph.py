from __future__ import annotations

import copy
from collections.abc import Hashable, Iterable, Iterator
from typing import Callable

from cached_graph_view import CachedDirectedGraphView
from exceptions import NodeDoesNotExistError
from subgraph_direction import SubgraphDirection

from graft.graphs2.directed_graph.ancestor_descendant_subgraph_view import (
    DirectedSubgraphView,
)

from ..bidict import BiDirectionalSetDict
from ..edges import EdgesView
from ..nodes import NodesView


class DirectedGraph[T: Hashable]:
    """Digraph with no parallel edges."""

    def __init__(self, bidict: BiDirectionalSetDict[T]) -> None:
        self._bidict = bidict

    def __bool__(self) -> bool:
        """Check if digraph is not empty."""
        return bool(self._bidict)

    def __eq__(self, other: object) -> bool:
        """Check if two digraphs are equal."""
        return (
            isinstance(other, DirectedGraph)
            and self.nodes() == other.nodes()
            and self.edges() == other.edges()
        )

    def __str__(self) -> str:
        """Return string representation of digraph."""
        return str(self._bidict)

    def __repr__(self) -> str:
        """Return string representation of digraph."""
        nodes_with_successors = (
            f"{node!r}: {{{', '.join(repr(successor) for successor in successors)}}}"
            for node, successors in self._bidict.items()
        )
        return f"{self.__class__.__name__}({{{', '.join(nodes_with_successors)}}})"

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        return len(self.predecessors(node))

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        return len(self.successors(node))

    def degree(self, node: T, /) -> int:
        """Return number of edges to and from node."""
        return self.in_degree(node) + self.out_degree(node)

    def add_node(self, node: T, /) -> None:
        """Add new node to digraph."""
        raise NotImplementedError

    def remove_node(self, node: T, /) -> None:
        """Remove existing node from digraph."""
        raise NotImplementedError

    def add_edge(self, source: T, target: T) -> None:
        """Add new edge to digraph."""
        raise NotImplementedError

    def remove_edge(self, source: T, target: T) -> None:
        """Remove existing edge from digraph."""
        raise NotImplementedError

    def nodes(self) -> NodesView[T]:
        """Return view of nodes in the digraph."""
        return NodesView(self._bidict.keys())

    def edges(self) -> EdgesView[T]:
        """Return view of digraph edges."""
        return EdgesView(self._bidict)

    def successors(self, node: T, /) -> NodesView[T]:
        """Return successors of node."""
        if node not in self.nodes():
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict[node])

    def predecessors(self, node: T, /) -> NodesView[T]:
        """Return predecessors of node."""
        if node not in self.nodes():
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict.inverse[node])

    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the descendants of nodes."""
        return DirectedSubgraphView(
            graph=self,
            direction=SubgraphDirection.DESCENDANT,
            starting_nodes=nodes,
            stop_condition=stop_condition,
        )

    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedSubgraphView[T]:
        """Return a subgraph of the ancestors of nodes."""
        return DirectedSubgraphView(
            graph=self,
            direction=SubgraphDirection.ANCESTOR,
            starting_nodes=nodes,
            stop_condition=stop_condition,
        )

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
        return copy.deepcopy(self)

    def cache(self) -> CachedDirectedGraphView[T]:
        """Create a cached view of the graph."""
        return CachedDirectedGraphView(self)

    def tee(self, n: int = 2) -> tuple[DirectedGraph[T], ...]:
        """Return a tuple of n independent graph views."""
        raise NotImplementedError
