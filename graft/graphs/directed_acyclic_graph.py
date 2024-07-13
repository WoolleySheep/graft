"""Acyclic digraph and associated Exceptions."""

import collections
from collections.abc import Generator, Hashable, Mapping, Set
from typing import Any, Literal

from graft.graphs import bidict as bd
from graft.graphs import simple_digraph


class UnderlyingDictHasCycleError[T: Hashable](Exception):
    """Underlying dictionary has a cycle."""

    def __init__(self, dictionary: Mapping[T, Set[T]]) -> None:
        """Initialize UnderlyingDictHasCycleError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has a cycle")


class InverseEdgeAlreadyExistsError[T: Hashable](Exception):
    """Inverse edge already exists."""

    def __init__(
        self,
        source: T,
        target: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InverseEdgeAlreadyExistsError."""
        self.source = source
        self.target = target
        super().__init__(
            f"inverse edge [{target}] -> [{source}] already exists",
            *args,
            **kwargs,
        )


class IntroducesCycleError[T: Hashable, G: "DirectedAcyclicGraph"](Exception):
    """Adding the edge introduces a cycle to the graph."""

    def __init__(
        self,
        source: T,
        target: T,
        connecting_subgraph: G,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize IntroducesCycleError."""
        self.source = source
        self.target = target
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"edge [{source}] -> [{target}] introduces cycle",
            *args,
            **kwargs,
        )


class DirectedAcyclicGraph[T: Hashable](simple_digraph.SimpleDiGraph[T]):
    """Simple Digraph with no cycles."""

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize DirectedAcyclicGraph."""
        super().__init__(bidict=bidict)

        if super().has_cycle():
            raise UnderlyingDictHasCycleError(dictionary=self._bidict)

    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        super().validate_edge_can_be_added(source, target)

        if (target, source) in self.edges():
            raise InverseEdgeAlreadyExistsError(source=target, target=source)

        if self.has_path(source=target, target=source):
            connecting_subgraph = self.connecting_subgraph(source=target, target=source)
            raise IntroducesCycleError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            )

    def has_cycle(self) -> Literal[False]:
        """Check if the graph has a cycle.

        Will always return False for a DAG.
        """
        return False

    def topological_sort_with_grouping(self) -> Generator[set[T], None, None]:
        """Return groups of nodes in topologically sorted order.

        Nodes should be in the lowest group possible.
        """
        # Calculate the group number of each node
        queue = collections.deque[T](self.roots())
        node_group_num = dict[T, int]((node, 0) for node in queue)
        while queue:
            node = queue.popleft()
            min_successor_group_num = node_group_num[node] + 1
            for successor in self.successors(node):
                if (
                    successor in node_group_num
                    and node_group_num[successor] >= min_successor_group_num
                ):
                    continue

                node_group_num[successor] = min_successor_group_num
                queue.append(successor)

        # Get the nodes in each group
        group_nodes = collections.defaultdict[int, set[T]](set[T])
        for node, group in node_group_num.items():
            group_nodes[group].add(node)

        # Yield node groups from lowest to highest
        for group, _ in enumerate(group_nodes):
            yield group_nodes[group]

    def has_redundant_edges(self) -> bool:
        """Check if graph has edges that are not required for a reduced DAG."""
        # TODO: Speed up using dynamic programming
        for source, target in self.edges():
            for successor in self.successors(source):
                if successor == target:
                    continue
                if self.has_path(source=successor, target=target):
                    return True

        return False
