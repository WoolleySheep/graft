"""Acyclic digraph and associated Exceptions."""

from __future__ import annotations

import collections
from collections.abc import Callable, Generator, Hashable, Iterable, Mapping, Set
from typing import Any, Literal, override

from graft.graphs import bidict as bd
from graft.graphs import directed_graph, simple_directed_graph


class UnderlyingDictHasCycleError[T: Hashable](Exception):
    """Underlying dictionary has a cycle."""

    def __init__(self, dictionary: Mapping[T, Set[T]]) -> None:
        """Initialize UnderlyingDictHasCycleError."""
        self.dictionary = dict(dictionary)
        super().__init__(f"underlying dictionary [{dictionary}] has a cycle")


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


class MultipleStartingNodesDirectedAcyclicSubgraphView[T: Hashable](
    simple_directed_graph.MultipleStartingNodesSimpleDirectedSubgraphView[T]
):
    """Directed acyclic subgraph view with multiple starting nodes."""

    @override
    def subgraph(self) -> DirectedAcyclicGraph[T]:
        subgraph = DirectedAcyclicGraph[T]()
        self._populate_graph(graph=subgraph)
        return subgraph


class SingleStartingNodeDirectedAcyclicSubgraphView[T: Hashable](
    simple_directed_graph.SingleStartingNodeSimpleDirectedSubgraphView[T]
):
    """Directed acyclic subgraph view with a single starting node."""

    @override
    def subgraph(self) -> DirectedAcyclicGraph[T]:
        subgraph = DirectedAcyclicGraph[T]()
        self._populate_graph(graph=subgraph)
        return subgraph


class DirectedAcyclicGraph[T: Hashable](simple_directed_graph.SimpleDirectedGraph[T]):
    """Simple Digraph with no cycles."""

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize DirectedAcyclicGraph."""
        super().__init__(bidict=bidict)

        if super().has_cycle():
            raise UnderlyingDictHasCycleError(dictionary=self._bidict)

    @override
    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        super().validate_edge_can_be_added(source, target)

        if self.has_path(source=target, target=source):
            connecting_subgraph = self.connecting_subgraph(source=target, target=source)
            raise IntroducesCycleError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            )

    @override
    def descendants(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> SingleStartingNodeDirectedAcyclicSubgraphView[T]:
        return SingleStartingNodeDirectedAcyclicSubgraphView(
            node, self._bidict, directed_graph.SubgraphType.DESCENDANTS, stop_condition
        )

    @override
    def descendants_multi(
        self,
        nodes: Iterable[T],
        /,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> MultipleStartingNodesDirectedAcyclicSubgraphView[T]:
        return MultipleStartingNodesDirectedAcyclicSubgraphView(
            nodes, self._bidict, directed_graph.SubgraphType.DESCENDANTS, stop_condition
        )

    @override
    def ancestors(
        self, node: T, /, stop_condition: Callable[[T], bool] | None = None
    ) -> SingleStartingNodeDirectedAcyclicSubgraphView[T]:
        return SingleStartingNodeDirectedAcyclicSubgraphView(
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
    ) -> MultipleStartingNodesDirectedAcyclicSubgraphView[T]:
        return MultipleStartingNodesDirectedAcyclicSubgraphView(
            nodes, self._bidict, directed_graph.SubgraphType.ANCESTORS, stop_condition
        )

    @override
    def has_cycle(self) -> Literal[False]:
        """Check if the graph has a cycle.

        Will always return False for a DAG.
        """
        return False

    def topologically_sorted_groups(self) -> Generator[set[T], None, None]:
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

    @override
    def connecting_subgraph(self, source: T, target: T) -> DirectedAcyclicGraph[T]:
        """Return connecting subgraph from source to target."""
        return self.connecting_subgraph_multi([source], [target])

    @override
    def connecting_subgraph_multi(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> DirectedAcyclicGraph[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        subgraph = DirectedAcyclicGraph[T]()
        self._populate_graph_with_connecting(
            graph=subgraph, sources=sources, targets=targets
        )
        return subgraph
