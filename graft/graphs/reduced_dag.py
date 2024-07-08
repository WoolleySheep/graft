"""Reduced DAG and associated Exceptions."""

from __future__ import annotations

from collections.abc import Hashable, Mapping, Set
from typing import Any, Literal

from graft.graphs import bidict as bd
from graft.graphs import directed_acyclic_graph, simple_digraph


class UnderlyingDictHasSuperfluousEdgesError[T: Hashable](Exception):
    """Underlying dictionary has superfluous edges."""

    def __init__(self, dictionary: Mapping[T, Set[T]]) -> None:
        """Initialize UnderlyingDictHasSuperfluousEdgesError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has superfluous edges")


class PathAlreadyExistsError[T: Hashable](Exception):
    """Path already exists from source to target."""

    def __init__(
        self,
        source: T,
        target: T,
        connecting_subgraph: ReducedDAG[T],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize PathAlreadyExistsError."""
        self.source = source
        self.target = target
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"path already exists between [{source}] and [{target}]",
            *args,
            **kwargs,
        )


class TargetAlreadySuccessorOfSourceAncestorsError[T: Hashable](Exception):
    """Target is already a successor of one or more of source's ancestors.

    The relevant ancestors are the roots of the subgraph.
    """

    def __init__(
        self,
        source: T,
        target: T,
        subgraph: ReducedDAG[T],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize TargetAlreadySuccessorOfSourceAncestorsError."""
        self.source = source
        self.target = target
        self.subgraph = subgraph
        super().__init__(
            (
                f"target [{target}] is already a successor of one or more of "
                f"source [{source}]'s ancestors"
            ),
            *args,
            **kwargs,
        )


class ReducedDAG[T: Hashable](directed_acyclic_graph.DirectedAcyclicGraph[T]):
    """Transitive reduction of a DAG, that does not have any superfluous edges.

    Only the minimal number of edges to describe the graph is allowed.
    """

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize ReducedDAG."""
        super().__init__(bidict=bidict)

        dag = directed_acyclic_graph.DirectedAcyclicGraph(bidict=bidict)
        if dag.has_superfluous_edges():
            raise UnderlyingDictHasSuperfluousEdgesError(dictionary=self._bidict)

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to minimal digraph."""
        if (source, target) in self.edges():
            raise simple_digraph.EdgeAlreadyExistsError(source=source, target=target)

        if (target, source) in self.edges():
            raise directed_acyclic_graph.InverseEdgeAlreadyExistsError(
                source=target,
                target=source,
            )

        if self.has_path(source=target, target=source):
            connecting_subgraph = self.connecting_subgraph(source=target, target=source)
            raise directed_acyclic_graph.IntroducesCycleError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            )

        if self.has_path(source=source, target=target):
            connecting_subgraph = self.connecting_subgraph(source=source, target=target)
            raise PathAlreadyExistsError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            )

        target_predecessors = self.predecessors(target)
        if any(
            source_ancestor in target_predecessors
            for source_ancestor in self.ancestors_bfs(source)
        ):
            source_ancestors_subgraph = self.ancestors_subgraph(
                source, stop_condition=lambda node: node in target_predecessors
            )
            target_predecessors_in_subgraph = (
                predecessor
                for predecessor in target_predecessors
                if predecessor in source_ancestors_subgraph
            )
            subgraph = source_ancestors_subgraph.descendants_subgraph_multi(
                target_predecessors_in_subgraph
            )
            raise TargetAlreadySuccessorOfSourceAncestorsError(
                source=source,
                target=target,
                subgraph=subgraph,
            )

        super().add_edge(source=source, target=target)

    def has_superfluous_edges(self) -> Literal[False]:
        return False
