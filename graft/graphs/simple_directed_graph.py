"""Simple DiGraph and associated Exceptions."""

from __future__ import annotations

from collections.abc import (
    Hashable,
    Iterable,
    Mapping,
    Set,
)
from typing import Any, Callable, Literal, override

from graft.graphs import bidict as bd
from graft.graphs import directed_graph


class UnderlyingDictHasLoopsError[T: Hashable](Exception):
    """Underlying dictionary has loops."""

    def __init__(self, dictionary: Mapping[T, Set[T]]) -> None:
        """Initialize UnderlyingDictHasLoopsError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has loop(s)")


class LoopError[T: Hashable](Exception):
    """Loop error.

    Raised when an edge is referenced that connects a node to itself, creating a
    loop. These aren't allowed in simple digraphs.
    """

    def __init__(
        self,
        node: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize LoopError."""
        self.node = node
        super().__init__(f"loop [{node}]", *args, **kwargs)


class MultipleStartingNodesSimpleDirectedSubgraphView[T: Hashable](
    directed_graph.MultipleStartingNodesSubgraphView[T]
):
    """Simple digraph subgraph view with multiple starting nodes."""

    @override
    def subgraph(self) -> SimpleDirectedGraph[T]:
        subgraph = SimpleDirectedGraph[T]()
        self._populate_graph(graph=subgraph)
        return subgraph


class SingleStartingNodeSimpleDirectedSubgraphView[T: Hashable](
    directed_graph.SingleStartingNodeSubgraphView[T]
):
    """Simple digraph subgraph view with a single starting node."""

    @override
    def subgraph(self) -> SimpleDirectedGraph[T]:
        subgraph = SimpleDirectedGraph[T]()
        self._populate_graph(graph=subgraph)
        return subgraph


class SimpleDirectedGraph[T: Hashable](directed_graph.DirectedGraph[T]):
    """Digraph with no loops or parallel edges."""

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize simple digraph."""
        super().__init__(bidict=bidict)

        # TODO: Think of a a different exception, seeing as this is occurring in
        # the initialiser
        for node, successors in self._bidict.items():
            if node in successors:
                raise UnderlyingDictHasLoopsError(dictionary=self._bidict)

    @override
    def descendants(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> SingleStartingNodeSimpleDirectedSubgraphView[T]:
        return SingleStartingNodeSimpleDirectedSubgraphView(
            node, self._bidict, directed_graph.SubgraphType.DESCENDANTS, stop_condition
        )

    @override
    def descendants_multi(
        self,
        nodes: Iterable[T],
        /,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> MultipleStartingNodesSimpleDirectedSubgraphView[T]:
        return MultipleStartingNodesSimpleDirectedSubgraphView(
            nodes, self._bidict, directed_graph.SubgraphType.DESCENDANTS, stop_condition
        )

    @override
    def ancestors(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> SingleStartingNodeSimpleDirectedSubgraphView[T]:
        return SingleStartingNodeSimpleDirectedSubgraphView(
            node,
            self._bidict,
            directed_graph.SubgraphType.ANCESTORS,
            stop_condition,
        )

    @override
    def ancestors_multi(
        self,
        nodes: Iterable[T],
        /,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> MultipleStartingNodesSimpleDirectedSubgraphView[T]:
        return MultipleStartingNodesSimpleDirectedSubgraphView(
            nodes, self._bidict, directed_graph.SubgraphType.ANCESTORS, stop_condition
        )

    @override
    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        super().validate_edge_can_be_added(source=source, target=target)

        if source == target:
            raise LoopError(node=source)

    @override
    def has_loop(self) -> Literal[False]:
        """Check if the graph has a loop.

        Will always return False for a simple digraph.
        """
        return False

    @override
    def remove_edge(self, source: T, target: T) -> None:
        try:
            super().remove_edge(source=source, target=target)
        except directed_graph.EdgeDoesNotExistError as e:
            if e.source == e.target:
                raise LoopError(node=e.source) from e

            raise

    @override
    def connecting_subgraph(self, source: T, target: T) -> SimpleDirectedGraph[T]:
        return self.connecting_subgraph_multi([source], [target])

    @override
    def connecting_subgraph_multi(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> SimpleDirectedGraph[T]:
        subgraph = SimpleDirectedGraph[T]()
        self._populate_graph_with_connecting(
            graph=subgraph, sources=sources, targets=targets
        )
        return subgraph
