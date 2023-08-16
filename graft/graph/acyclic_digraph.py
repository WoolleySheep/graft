"""DiGraph and associated Exceptions."""

import collections
from collections.abc import Hashable, Iterator
from typing import Any, TypeVar

from graft.graph import digraph

T = TypeVar("T", bound=Hashable)


class LoopError(Exception):
    """Loop error.

    Raised when edge created from node to itself, creating a loop.
    """

    def __init__(
        self,
        node: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize SelfLoopError."""
        self.node = node
        super().__init__(f"loop [{node}]", *args, **kwargs)


class InverseEdgeAlreadyExistsError(Exception):
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


class IntroducesCycleError(Exception):
    """Adding the edge introduces a cycle to the graph."""

    def __init__(
        self,
        source: T,
        target: T,
        cyclic_subgraph: digraph.DiGraph[T],
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


class AcyclicDiGraph(digraph.DiGraph[T]):
    """Directed graph with no cycles."""

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to Acyclic DiGraph."""
        if source == target:
            raise LoopError(node=source)

        if self._has_edge(source, target):
            raise digraph.EdgeAlreadyExistsError(source=source, target=target)

        if self._has_edge(source=target, target=source):
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

    def topological_sort_with_grouping(self) -> Iterator[set[T]]:
        """Return groups of nodes in topologically sorted order.

        Nodes should be in the lowest group possible.
        """
        # Calculate the group number of each node
        queue = collections.deque(self.roots())
        node_group = {node: 0 for node in queue}
        while queue:
            node = queue.popleft()
            min_successor_group = node_group[node] + 1
            for successor in self.successors(node):
                if (
                    successor in node_group
                    and node_group[successor] >= min_successor_group
                ):
                    continue

                node_group[successor] = min_successor_group
                queue.append(successor)

        # Get the nodes in each group
        group_nodes: collections.defaultdict[int, set[T]] = collections.defaultdict(set)
        for node, group in node_group.items():
            group_nodes[group].add(node)

        # Yield node groups from lowest to highest
        for group in range(len(group_nodes)):
            yield group_nodes[group]
