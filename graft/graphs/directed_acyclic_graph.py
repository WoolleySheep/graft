"""Acyclic digraph and associated Exceptions."""

from __future__ import annotations

import collections
from collections.abc import (
    Callable,
    Collection,
    Generator,
    Hashable,
    Iterable,
    Mapping,
    MutableMapping,
    Set,
)
from typing import Any, Literal, override

from graft.graphs import simple_directed_graph


class ConnectionsDictHasCycleError(Exception):
    """Underlying dictionary has a cycle."""

    def __init__(self, dictionary: Mapping[Any, Set[Any]]) -> None:
        self.dictionary = dict(dictionary)
        super().__init__(f"Underlying dictionary [{dictionary}] has a cycle")


class IntroducesCycleError(Exception):
    """Adding the edge introduces a cycle to the graph."""

    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        connecting_subgraph: DirectedAcyclicGraph[Any],
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


class DirectedAcyclicSubgraphBuilder[T: Hashable](
    simple_directed_graph.SimpleDirectedSubgraphBuilder[T]
):
    """Builder for a subgraph of a simple directed graph."""

    def __init__(self, graph: DirectedAcyclicGraph[T]) -> None:
        super().__init__(graph)

    @override
    def build(self) -> DirectedAcyclicGraph[T]:
        return DirectedAcyclicGraph(self._graph_builder.build().items())


class DirectedAcyclicGraph[T: Hashable](simple_directed_graph.SimpleDirectedGraph[T]):
    """Simple Digraph with no cycles."""

    def __init__(
        self, connections: Iterable[tuple[T, Iterable[T]]] | None = None
    ) -> None:
        """Initialize DirectedAcyclicGraph."""
        super().__init__(connections=connections)

        if super().has_cycle():
            # TODO: Get the exact dictionary elements that form the cycle
            raise ConnectionsDictHasCycleError(dictionary=self._bidict)

    @override
    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        super().validate_edge_can_be_added(source, target)

        if source in self.descendants([target]):
            connecting_subgraph = self.connecting_subgraph(
                sources=[target], targets=[source]
            )
            raise IntroducesCycleError(
                source=source,
                target=target,
                connecting_subgraph=connecting_subgraph,
            )

    @override
    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedAcyclicGraph[T]:
        builder = DirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_descendants_subgraph(nodes, stop_condition)
        return builder.build()

    @override
    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedAcyclicGraph[T]:
        builder = DirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_ancestors_subgraph(nodes, stop_condition)
        return builder.build()

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

        class LazyAncestors:
            """Lazily iteration and membership testing, with dynamic accumulation."""

            def __init__(
                self,
                node: T,
                node_predecessors_map: Mapping[T, Collection[T]],
                node_ancestors_map: MutableMapping[T, LazyAncestors],
            ) -> None:
                self._node_predecessors_map = node_predecessors_map
                self._node_ancestors_map = node_ancestors_map

                self._predecessors_unprocessed = collections.deque(
                    node_predecessors_map[node]
                )
                self._ancestors = set(node_predecessors_map[node])

            def _get_ancestors(self, node: T) -> LazyAncestors:
                if node in self._node_ancestors_map:
                    return self._node_ancestors_map[node]

                ancestors = LazyAncestors(
                    node=node,
                    node_predecessors_map=self._node_predecessors_map,
                    node_ancestors_map=self._node_ancestors_map,
                )
                self._node_ancestors_map[node] = ancestors
                return ancestors

            def __iter__(self) -> Generator[T, None, None]:
                yield from self._ancestors

                while self._predecessors_unprocessed:
                    predecessor = self._predecessors_unprocessed[0]
                    predecessor_ancestors = self._get_ancestors(predecessor)
                    for predecessor_ancestor in predecessor_ancestors:
                        if predecessor_ancestor in self._ancestors:
                            continue
                        yield predecessor_ancestor
                    self._ancestors.update(predecessor_ancestors)
                    _ = self._predecessors_unprocessed.popleft()

            def __contains__(self, node: T) -> bool:
                if node in self._ancestors:
                    return True

                while self._predecessors_unprocessed:
                    predecessor = self._predecessors_unprocessed[0]
                    predecessor_ancestors = self._get_ancestors(predecessor)
                    if node in predecessor_ancestors:
                        return True
                    self._ancestors.update(predecessor_ancestors)
                    _ = self._predecessors_unprocessed.popleft()

                return False

        def get_ancestors(
            node: T,
            node_predecessors_map: Mapping[T, Collection[T]],
            node_ancestors_map: MutableMapping[T, LazyAncestors],
        ) -> LazyAncestors:
            if node in node_ancestors_map:
                return node_ancestors_map[node]

            ancestors = LazyAncestors(
                node,
                node_predecessors_map=node_predecessors_map,
                node_ancestors_map=node_ancestors_map,
            )
            node_ancestors_map[node] = ancestors
            return ancestors

        node_ancestors_map = dict[T, LazyAncestors]()

        for source, target in self.edges():
            target_ancestors = get_ancestors(
                target,
                node_predecessors_map=self._bidict.inverse,
                node_ancestors_map=node_ancestors_map,
            )
            for successor in self.successors(source):
                if successor not in target_ancestors:
                    continue

                return True

        return False

    @override
    def connecting_subgraph(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> DirectedAcyclicGraph[T]:
        builder = DirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_connecting_subgraph(sources, targets)
        return builder.build()

    @override
    def component_subgraph(self, node: T) -> DirectedAcyclicGraph[T]:
        builder = DirectedAcyclicSubgraphBuilder[T](self)
        _ = builder.add_component_subgraph(node)
        return builder.build()

    @override
    def component_subgraphs(self) -> Generator[DirectedAcyclicGraph[T], None, None]:
        """Yield component subgraphs in the graph."""
        checked_nodes = set[T]()
        for node in self.nodes():
            if node in checked_nodes:
                continue

            component = self.component_subgraph(node)
            checked_nodes.update(component.nodes())
            yield component
