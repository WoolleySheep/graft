"""Minimal DAG and associated Exceptions."""

from __future__ import annotations

import collections
from collections.abc import Hashable
from typing import Any, Self

from graft.graphs import directed_acyclic_graph, simple_digraph


class PathAlreadyExistsError[T: Hashable](Exception):
    """Path already exists from source to target."""

    def __init__(
        self,
        source: T,
        target: T,
        connecting_subgraph: MinimumDAG[T],
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
        subgraph: MinimumDAG[T],
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


class MinimumDAG[T: Hashable](directed_acyclic_graph.DirectedAcyclicGraph[T]):
    """A DAG that does not have any superfluous edges.

    Only the minimal number of edges to describe the graph is allowed.
    """

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to minimal digraph."""

        def get_target_predecessor_is_source_ancestor_subgraph(
            self: Self,
            source: T,
            target: T,
        ) -> Self:
            """Return ancestors of source that are also predecessors of target."""

            def get_ancestor_subgraph(
                digraph: Self,
                source: T,
                target: T,
            ) -> tuple[set[T], Self]:
                """Return subgraph of target-predecessor ancestors.

                Generate a subgraph of all ancestors of source, stopping
                whenever you encounter an ancestor that is a predecessor of
                target.
                """
                target_predecessors = set[T](digraph.predecessors(target))
                subgraph = type(self)()
                subgraph.add_node(source)
                ancestors_of_interest = set[T]()
                ancestors_visited = set[T]()
                queue = collections.deque[T]([source])

                while queue:
                    node = queue.popleft()

                    if node in ancestors_visited:
                        continue
                    ancestors_visited.add(node)

                    if node in target_predecessors:
                        ancestors_of_interest.add(node)
                        continue

                    for predecessor in digraph.predecessors(node):
                        if predecessor not in subgraph:
                            subgraph.add_node(predecessor)
                        subgraph.add_edge(predecessor, node)
                        queue.append(predecessor)

                return ancestors_of_interest, subgraph

            for node in [source, target]:
                if node not in self:
                    raise simple_digraph.NodeDoesNotExistError(node=node)

            # Generate a subgraph of all ancestors, stopping whenever you encounter
            # an ancestor that is a predecessor of target.
            ancestors_of_interest: set[T]
            ancestor_subgraph: Self
            ancestors_of_interest, ancestor_subgraph = get_ancestor_subgraph(
                digraph=self,
                source=source,
                target=target,
            )

            # Retrace the path from each of the ancestors of interest, joining these
            # into one subgraph. As ancestors_subgraph started from source, it will
            # be the only leaf node. None of the ancestors of interest will be in
            # each other's path to source.
            return ancestor_subgraph.descendants_subgraph_multi(
                nodes=ancestors_of_interest
            )

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
            subgraph = get_target_predecessor_is_source_ancestor_subgraph(
                self=self,
                source=source,
                target=target,
            )
            raise TargetAlreadySuccessorOfSourceAncestorsError(
                source=source,
                target=target,
                subgraph=subgraph,
            )

        super().add_edge(source=source, target=target)
