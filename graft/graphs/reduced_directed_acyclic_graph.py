"""Reduced DAG and associated Exceptions."""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Mapping, Set
from typing import Any, Literal, override

from graft.graphs import bidict as bd
from graft.graphs import directed_acyclic_graph, directed_graph


class UnderlyingDictHasRedundantEdgesError[T: Hashable](Exception):
    """Underlying dictionary has redundant edges."""

    def __init__(self, dictionary: Mapping[T, Set[T]]) -> None:
        """Initialize UnderlyingDictHasRedundantEdgesError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has redundant edges")


class IntroducesRedundantEdgeError[T: Hashable](Exception):
    """Adding the edge introduces a redundant edge to the graph."""

    def __init__(
        self,
        source: T,
        target: T,
        subgraph: ReducedDirectedAcyclicGraph[T],
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


class ReducedDirectedAcyclicSubgraphView[T: Hashable](
    directed_acyclic_graph.DirectedAcyclicSubgraphView[T]
):
    """Simple digraph subgraph view."""

    @override
    def subgraph(
        self, include_starting_node: bool = False
    ) -> ReducedDirectedAcyclicGraph[T]:
        subgraph = ReducedDirectedAcyclicGraph[T]()
        self._populate_graph(
            graph=subgraph, include_starting_node=include_starting_node
        )
        return subgraph


class ReducedDirectedAcyclicGraph[T: Hashable](
    directed_acyclic_graph.DirectedAcyclicGraph[T]
):
    """Transitive reduction of a DAG, that does not have any redundant edges.

    Only the minimal number of edges to describe the graph is allowed.
    """

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize ReducedDAG."""
        super().__init__(bidict=bidict)

        if super().has_redundant_edges():
            raise UnderlyingDictHasRedundantEdgesError(dictionary=self._bidict)

    @override
    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        super().validate_edge_can_be_added(source=source, target=target)

        if self.has_path(source=source, target=target):
            subgraph = self.connecting_subgraph(source=source, target=target)
            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=subgraph
            )

        target_predecessors = self.predecessors(target)
        if any(
            source_ancestor in target_predecessors
            for source_ancestor in self.ancestors(source).nodes()
        ):
            source_ancestors_subgraph = self.ancestors(
                source, stop_condition=lambda node: node in target_predecessors
            ).subgraph(include_starting_node=True)
            target_predecessors_in_subgraph = [
                predecessor
                for predecessor in target_predecessors
                if predecessor in source_ancestors_subgraph.nodes()
            ]
            subgraph = source_ancestors_subgraph.descendants_subgraph_multi(
                target_predecessors_in_subgraph
            )
            subgraph.add_node(target)
            for target_predecessor in target_predecessors_in_subgraph:
                subgraph.add_edge(target_predecessor, target)
            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=subgraph
            )

        source_successors = self.successors(source)
        if any(
            target_descendant in source_successors
            for target_descendant in self.descendants(target).nodes()
        ):
            target_descendants_subgraph = self.descendants(
                target, stop_condition=lambda node: node in source_successors
            ).subgraph(include_starting_node=True)
            source_successors_in_subgraph = [
                successor
                for successor in source_successors
                if successor in target_descendants_subgraph.nodes()
            ]
            subgraph = target_descendants_subgraph.ancestors_subgraph_multi(
                source_successors_in_subgraph
            )
            subgraph.add_node(source)
            for source_successor in source_successors_in_subgraph:
                subgraph.add_edge(source, source_successor)
            raise IntroducesRedundantEdgeError(
                source=source, target=target, subgraph=subgraph
            )

    @override
    def descendants(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicSubgraphView[T]:
        return ReducedDirectedAcyclicSubgraphView(
            node, self._bidict, directed_graph.SubgraphType.DESCENDANTS, stop_condition
        )

    @override
    def ancestors(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicSubgraphView[T]:
        return ReducedDirectedAcyclicSubgraphView(
            node,
            self._bidict.inverse,
            directed_graph.SubgraphType.ANCESTORS,
            stop_condition,
        )

    @override
    def has_redundant_edges(self) -> Literal[False]:
        """Check if graph has edges that are not required for a reduced DAG.

        Will always return False for a reduced DAG.
        """
        return False

    @override
    def descendants_subgraph_multi(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicGraph[T]:
        """Return a subgraph of the descendants of multiple nodes.

        This effectively OR's together the descendant subgraphs of several
        nodes.

        The original nodes are part of the subgraph.

        Stop searching beyond a specific node if the stop condition is met.
        """
        subgraph = ReducedDirectedAcyclicGraph[T]()
        self._populate_graph_with_descendants(
            graph=subgraph, nodes=nodes, stop_condition=stop_condition
        )
        return subgraph

    @override
    def ancestors_subgraph_multi(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> ReducedDirectedAcyclicGraph[T]:
        """Return a subgraph of the ancestors of multiple nodes.

        This effectively OR's together the ancestor subgraphs of several
        nodes.

        The original nodes are part of the subgraph.

        Stop searching beyond a specific node if the stop condition is met.
        """
        subgraph = ReducedDirectedAcyclicGraph[T]()
        self._populate_graph_with_ancestors(
            graph=subgraph, nodes=nodes, stop_condition=stop_condition
        )
        return subgraph

    @override
    def connecting_subgraph(
        self, source: T, target: T
    ) -> ReducedDirectedAcyclicGraph[T]:
        """Return connecting subgraph from source to target."""
        return self.connecting_subgraph_multi([source], [target])

    @override
    def connecting_subgraph_multi(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> ReducedDirectedAcyclicGraph[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        subgraph = ReducedDirectedAcyclicGraph[T]()
        self._populate_graph_with_connecting(
            graph=subgraph, sources=sources, targets=targets
        )
        return subgraph