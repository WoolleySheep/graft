"""Simple DiGraph and associated Exceptions."""

from __future__ import annotations

from collections.abc import (
    Generator,
    Hashable,
    Iterable,
)
from typing import Any, Callable, Literal, override

from graft.graphs import directed_graph


class ConnectionsDictNodesHaveLoops(Exception):
    """Connections used to construct the graph include loops."""

    def __init__(self, nodes: Iterable[Hashable]) -> None:
        self.nodes = set(nodes)
        formatted_nodes = (str(node) for node in self.nodes)
        super().__init__(
            f"Connections used to construct the graph have loops for nodes [{', '.join(formatted_nodes)}]"
        )


class LoopError(Exception):
    """Loop error.

    Raised when an edge is referenced that connects a node to itself, creating a
    loop. These aren't allowed in simple digraphs.
    """

    def __init__(
        self,
        node: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize LoopError."""
        self.node = node
        super().__init__(f"loop [{node}]", *args, **kwargs)


class SimpleDirectedSubgraphBuilder[T: Hashable](
    directed_graph.DirectedSubgraphBuilder[T]
):
    """Builder for a subgraph of a simple directed graph."""

    def __init__(self, graph: SimpleDirectedGraph[T]) -> None:
        super().__init__(graph)

    @override
    def build(self) -> SimpleDirectedGraph[T]:
        return SimpleDirectedGraph(self._graph_builder.build().items())


class SimpleDirectedGraph[T: Hashable](directed_graph.DirectedGraph[T]):
    """Digraph with no loops or parallel edges."""

    def __init__(
        self, connections: Iterable[tuple[T, Iterable[T]]] | None = None
    ) -> None:
        """Initialize simple digraph."""
        super().__init__(connections=connections)

        nodes_with_loops = set[T]()
        for node in self.nodes():
            if node in self.successors(node):
                nodes_with_loops.add(node)

        if nodes_with_loops:
            raise ConnectionsDictNodesHaveLoops(nodes=nodes_with_loops)

    @override
    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> SimpleDirectedGraph[T]:
        builder = SimpleDirectedSubgraphBuilder[T](self)
        builder.add_descendants_subgraph(nodes, stop_condition)
        return builder.build()

    @override
    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> SimpleDirectedGraph[T]:
        builder = SimpleDirectedSubgraphBuilder[T](self)
        _ = builder.add_ancestors_subgraph(nodes, stop_condition)
        return builder.build()

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
    def connecting_subgraph(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> SimpleDirectedGraph[T]:
        builder = SimpleDirectedSubgraphBuilder[T](self)
        _ = builder.add_connecting_subgraph(sources, targets)
        return builder.build()

    @override
    def component_subgraph(self, node: T) -> SimpleDirectedGraph[T]:
        builder = SimpleDirectedSubgraphBuilder[T](self)
        _ = builder.add_component_subgraph(node)
        return builder.build()

    @override
    def component_subgraphs(self) -> Generator[SimpleDirectedGraph[T], None, None]:
        """Yield component subgraphs in the graph."""
        checked_nodes = set[T]()
        for node in self.nodes():
            if node in checked_nodes:
                continue

            component = self.component_subgraph(node)
            checked_nodes.update(component.nodes())
            yield component
