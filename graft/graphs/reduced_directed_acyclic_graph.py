"""Reduced DAG and associated Exceptions."""

from __future__ import annotations

from collections.abc import Callable, Generator, Hashable, Iterable, Mapping, Set
from typing import Any, Literal, override

from graft.graphs import directed_acyclic_graph
from graft.utils import LazyContainer


class UnderlyingDictHasRedundantEdgesError(Exception):
    """Underlying dictionary has redundant edges."""

    def __init__(self, dictionary: Mapping[Any, Set[Any]]) -> None:
        """Initialize UnderlyingDictHasRedundantEdgesError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has redundant edges")


class IntroducesRedundantEdgeError(Exception):
    """Adding the edge introduces a redundant edge to the graph."""

    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        subgraph: ReducedDirectedAcyclicGraph[Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize IntroduceReduntantEdgeError."""
        self.source = source
        self.target = target
        self.subgraph = subgraph
        super().__init__(
            f"introducing redundant edge from [{source}] to [{target}]", *args, **kwargs
        )


class IntroducesCycleToReducedGraphError(Exception):
    """Adding the edge introduces a cycle to the graph."""

    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        connecting_subgraph: ReducedDirectedAcyclicGraph[Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize IntroducesCycleError."""
        self.source = source
        self.target = target
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"edge [{source}] -> [{target}] introduces cycle to reduced graph",
            *args,
            **kwargs,
        )


class ReducedDirectedAcyclicSubgraphBuilder[T: Hashable](
    directed_acyclic_graph.DirectedAcyclicSubgraphBuilder[T]
):
    """Builder for a subgraph of a simple directed graph."""

    def __init__(self, graph: ReducedDirectedAcyclicGraph[T]) -> None:
        super().__init__(graph)

    @override
    def build(self) -> ReducedDirectedAcyclicGraph[T]:
        return ReducedDirectedAcyclicGraph(self._graph_builder.build().items())


class ReducedDirectedAcyclicGraph[T: Hashable](
    directed_acyclic_graph.DirectedAcyclicGraph[T]
):
    """Transitive reduction of a DAG, that does not have any redundant edges.

    Only the minimal number of edges to describe the graph is allowed.
    """

    def __init__(
        self, connections: Iterable[tuple[T, Iterable[T]]] | None = None
    ) -> None:
        """Initialize ReducedDAG."""
        super().__init__(connections=connections)

        if super().has_redundant_edges():
            # TODO: Get the redundant edges
            raise UnderlyingDictHasRedundantEdgesError(dictionary=self._bidict)

    @override
    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        try:
            super().validate_edge_can_be_added(source=source, target=target)
        except directed_acyclic_graph.IntroducesCycleError:
            # TODO: Fix this inefficient and kinda bad hack
            connecting_subgraph = self.connecting_subgraph(
                sources=[target], targets=[source]
            )
            raise IntroducesCycleToReducedGraphError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            ) from None

        if target in self.descendants([source]):
            connecting_subgraph = self.connecting_subgraph([source], [target])
            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=connecting_subgraph
            )

        if any(
            source_ancestor in self.predecessors(target)
            for source_ancestor in self.ancestors([source])
        ):
            source_ancestors = LazyContainer(
                self.ancestors(
                    [source],
                    stop_condition=lambda node: node in self.predecessors(target),
                )
            )
            target_predecessors_in_source_ancestors = [
                predecessor
                for predecessor in self.predecessors(target)
                if predecessor in source_ancestors
            ]
            subgraph_builder = ReducedDirectedAcyclicSubgraphBuilder(self)
            _ = subgraph_builder.add_descendants_subgraph(
                target_predecessors_in_source_ancestors
            )
            for target_predecessor in target_predecessors_in_source_ancestors:
                subgraph_builder.add_edge(target_predecessor, target)

            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=subgraph_builder.build()
            )

        if any(
            target_descendant in self.successors(source)
            for target_descendant in self.descendants([target])
        ):
            target_descendants = LazyContainer(
                self.descendants(
                    [target],
                    stop_condition=lambda node: node in self.successors(source),
                )
            )
            source_successors_in_target_descendants = [
                successor
                for successor in self.successors(source)
                if successor in target_descendants
            ]
            subgraph_builder = ReducedDirectedAcyclicSubgraphBuilder(self)
            _ = subgraph_builder.add_ancestors_subgraph(
                source_successors_in_target_descendants
            )
            for source_successor in source_successors_in_target_descendants:
                subgraph_builder.add_edge(source, source_successor)

            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=subgraph_builder.build()
            )

    @override
    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicGraph[T]:
        builder = ReducedDirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_descendants_subgraph(nodes, stop_condition)
        return builder.build()

    @override
    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicGraph[T]:
        builder = ReducedDirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_ancestors_subgraph(nodes, stop_condition)
        return builder.build()

    @override
    def has_redundant_edges(self) -> Literal[False]:
        """Check if graph has edges that are not required for a reduced DAG.

        Will always return False for a reduced DAG.
        """
        return False

    @override
    def connecting_subgraph(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> ReducedDirectedAcyclicGraph[T]:
        builder = ReducedDirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_connecting_subgraph(sources, targets)
        return builder.build()

    @override
    def component_subgraph(self, node: T) -> ReducedDirectedAcyclicGraph[T]:
        builder = ReducedDirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_component_subgraph(node)
        return builder.build()

    @override
    def component_subgraphs(
        self,
    ) -> Generator[ReducedDirectedAcyclicGraph[T], None, None]:
        """Yield component subgraphs in the graph."""
        checked_nodes = set[T]()
        for node in self.nodes():
            if node in checked_nodes:
                continue

            component = self.component_subgraph(node)
            checked_nodes.update(component.nodes())
            yield component
