"""Acyclic digraph and associated Exceptions."""

import collections
from collections.abc import Generator, Hashable
from typing import Any

from graft.graphs import simple_digraph


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


class IntroducesCycleError[T: Hashable](Exception):
    """Adding the edge introduces a cycle to the graph."""

    def __init__(
        self,
        source: T,
        target: T,
        cyclic_subgraph: simple_digraph.SimpleDiGraph[T],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize IntroducesCycleError."""
        self.source = source
        self.target = target
        self.cyclic_subgraph = cyclic_subgraph
        super().__init__(
            f"edge [{source}] -> [{target}] introduces cycle",
            *args,
            **kwargs,
        )


class DirectedAcyclicGraph[T: Hashable](simple_digraph.SimpleDiGraph[T]):
    """Simple Digraph with no cycles."""

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to graph."""
        if (source, target) in self.edges():
            raise simple_digraph.EdgeAlreadyExistsError(source=source, target=target)

        if (target, source) in self.edges():
            raise InverseEdgeAlreadyExistsError(source=target, target=source)

        if self.has_path(source=target, target=source):
            cyclic_subgraph = self.connecting_subgraph(source=target, target=source)
            cyclic_subgraph.add_edge(source=source, target=target)
            raise IntroducesCycleError(
                source=source,
                target=target,
                cyclic_subgraph=cyclic_subgraph,
            )

        return super().add_edge(source, target)

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
