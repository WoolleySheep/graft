"""Simple DiGraph and associated Exceptions."""

from __future__ import annotations

import collections
import itertools
from collections.abc import (
    Hashable,
    Set,
)
from typing import TYPE_CHECKING, Any, TypeGuard

from graft.graphs import bidict as bd
from graft.graphs.directed_graph_builder import DirectedGraphBuilder

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
        Iterable,
        Iterator,
        Mapping,
    )


class NodeAlreadyExistsError(Exception):
    """Raised when node already exists."""

    def __init__(
        self,
        node: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NodeAlreadyExistsError."""
        self.node = node
        super().__init__(f"node [{node}] already exists", *args, **kwargs)


class NodeDoesNotExistError(Exception):
    """Raised when node does not exist."""

    def __init__(
        self,
        node: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NodeDoesNotExistError."""
        self.node = node
        super().__init__(f"node [{node}] does not exist", *args, **kwargs)


class HasNeighboursError(Exception):
    """Raised when a task has neighbours.

    A node cannot be removed when it has any neighbours.
    """

    def __init__(
        self,
        node: Hashable,
        predecessors: Iterable[Hashable],
        successors: Iterable[Hashable],
    ) -> None:
        self.node = node
        self.predecessors = set(predecessors)
        self.successors = set(successors)
        formatted_neighbours = (
            str(neighbour)
            for neighbour in itertools.chain(self.predecessors, self.successors)
        )
        super().__init__(
            f"Node [{node}] has neighbours [{', '.join(formatted_neighbours)}]"
        )


class EdgeAlreadyExistsError(Exception):
    """Raised when edge already exists."""

    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize EdgeAlreadyExistsError."""
        self.source = source
        self.target = target
        super().__init__(
            f"edge [{source}] -> [{target}] already exists",
            *args,
            **kwargs,
        )


class EdgeDoesNotExistError(Exception):
    """Raised when edge does not exist."""

    def __init__(
        self,
        source: Hashable,
        target: Hashable,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize EdgeDoesNotExistError."""
        self.source = source
        self.target = target
        super().__init__(
            f"edge [{source}] -> [{target}] does not exist",
            *args,
            **kwargs,
        )


class NoConnectingSubgraphError(Exception):
    """Raised when no connecting subgraph exists between two set of nodes."""

    def __init__(
        self,
        sources: Iterable[Any],
        targets: Iterable[Any],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NoConnectingSubgraphError."""
        self.sources = list(sources)
        self.targets = list(targets)

        formatted_sources = ", ".join(str(source) for source in sources)
        formatted_targets = ", ".join(str(target) for target in targets)
        super().__init__(
            f"no connecting subgraph from [{formatted_sources}] to [{formatted_targets}] exists",
            *args,
            **kwargs,
        )


class TargetsAreNotNotAlsoSourceNodesError(Exception):
    """Raised when some targets are not also sources."""

    def __init__(
        self,
        targets: Iterable[Hashable],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.targets = set(targets)
        super().__init__(
            f"targets [{self.targets}] are not also sources", *args, **kwargs
        )


class NodesView[T: Hashable](Set[T]):
    """View of a set of nodes."""

    def __init__(self, nodes: Set[T], /) -> None:
        """Initialise NodesView."""
        self._nodes: Set[T] = nodes

    def __bool__(self) -> bool:
        """Check view has any nodes."""
        return bool(self._nodes)

    def __len__(self) -> int:
        """Return number of nodes in view."""
        return len(self._nodes)

    def __contains__(self, item: object) -> bool:
        """Check if item is in the view."""
        return item in self._nodes

    def __iter__(self) -> Iterator[T]:
        """Return iterator over nodes in view."""
        return iter(self._nodes)

    def __eq__(self, other: object) -> bool:
        """Check if views are equal."""
        if not isinstance(other, NodesView):
            return NotImplemented

        return set(self._nodes) == set(other)

    def __str__(self) -> str:
        """Return string representation of the nodes."""
        return f"{{{', '.join(str(node) for node in self)}}}"

    def __repr__(self) -> str:
        """Return string representation of the nodes."""
        return f"{self.__class__.__name__}{{{', '.join(repr(node) for node in self)}}}"

    def __sub__(self, other: Set[Any]) -> set[T]:
        """Return difference of two views."""
        return set(self._nodes - other)

    def __and__(self, other: Set[Any]) -> set[T]:
        """Return intersection of two views."""
        return set(self._nodes & other)

    def __or__[G: Hashable](self, other: Set[G]) -> set[T | G]:
        """Return union of two views."""
        return set(self._nodes | other)

    def __xor__[G: Hashable](self, other: Set[G]) -> set[T | G]:
        """Return symmetric difference of two views."""
        return set(self._nodes ^ other)

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return self._nodes <= other

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self._nodes < other

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return self._nodes >= other

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self._nodes > other


class EdgesView[T: Hashable](Set[tuple[T, T]]):
    """View of the edges of a graph."""

    def __init__(self, node_successors_map: Mapping[T, Set[T]], /) -> None:
        """Initialise EdgesView."""
        self._node_successors_map: Mapping[T, Set[T]] = node_successors_map

    def __bool__(self) -> bool:
        """Check view has any edges."""
        return any(self._node_successors_map.values())

    def __eq__(self, other: object) -> bool:
        """Check if view is equal to other."""
        if not isinstance(other, EdgesView):
            return NotImplemented

        return len(self) == len(other) and all(edge in other for edge in self)

    def __len__(self) -> int:
        """Return number of edges in view."""
        return sum(len(values) for values in self._node_successors_map.values())

    def __contains__(self, item: object) -> bool:
        """Check if item in EdgesView."""

        def is_two_element_tuple_of_hashables(item: object) -> TypeGuard[tuple[T, T]]:
            """Check if item is a two element tuple of type Hashable.

            Bit of a hack, as hashable counted as equivalent to type T (not
            strictly true). Done to get around impossibility of runtime checking
            of T.
            """
            return (
                isinstance(item, tuple)
                and len(item) == 2
                and all(isinstance(element, Hashable) for element in item)
            )

        if not is_two_element_tuple_of_hashables(item):
            return NotImplemented

        for node in item:
            if node not in self._node_successors_map:
                raise NodeDoesNotExistError(node=node)

        source, target = item
        return target in self._node_successors_map[source]

    def __iter__(self) -> Generator[tuple[T, T], None, None]:
        """Return generator over edges in view."""
        for node, successors in self._node_successors_map.items():
            for successor in successors:
                yield (node, successor)

    def __str__(self) -> str:
        """Return string representation of edges."""
        formatted_node_successor_pairs = (
            f"({node}, {successor})" for node, successor in self
        )
        return f"{{{', '.join(formatted_node_successor_pairs)}}}"

    def __repr__(self) -> str:
        """Return string representation of edges."""
        formatted_node_successor_pairs = (
            f"({node!r}, {successor!r})" for node, successor in self
        )
        return f"{self.__class__.__name__}({{{', '.join(formatted_node_successor_pairs)}}})"

    def __sub__(self, other: Set[Any]) -> set[tuple[T, T]]:
        """Return difference of two views."""
        return {edge for edge in self if edge not in other}

    def __and__(self, other: Set[Any]) -> set[tuple[T, T]]:
        """Return intersection of two views."""
        return {edge for edge in self if edge in other}

    def __or__[G: Hashable](self, other: Set[G]) -> set[tuple[T, T] | G]:
        """Return union of two views."""
        return {*self, *other}

    def __xor__[G: Hashable](self, other: Set[G]) -> set[tuple[T, T] | G]:
        """Return symmetric difference of two views."""
        return {
            *(edge for edge in self if edge not in other),
            *(edge for edge in other if edge not in self),
        }

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return all(edge in other for edge in self)

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self <= other and len(self) < len(other)

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return all(edge in self for edge in other)

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self >= other and len(self) > len(other)


class DirectedSubgraphBuilder[T: Hashable]:
    """Builder for a subgraph of a directed graph."""

    def __init__(self, graph: DirectedGraph[T]) -> None:
        self._graph = graph
        self._graph_builder = DirectedGraphBuilder[T]()

    def add_node(self, node: T, /) -> None:
        if node not in self._graph.nodes():
            raise NodeDoesNotExistError(node)

        self._graph_builder.add_node(node)

    def add_edge(self, source: T, target: T) -> None:
        if (source, target) not in self._graph.edges():
            raise EdgeDoesNotExistError(source=source, target=target)

        self._graph_builder.add_edge(source=source, target=target)

    def add_ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> set[T]:
        """Add an ancestors subgraph."""
        return self._graph_builder.add_ancestors_subgraph(
            nodes,
            get_predecessors=self._graph.predecessors,
            stop_condition=stop_condition,
        )

    def add_descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> set[T]:
        """Add a descendants subgraph."""
        return self._graph_builder.add_descendants_subgraph(
            nodes,
            get_successors=self._graph.successors,
            stop_condition=stop_condition,
        )

    def add_connecting_subgraph(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> set[T]:
        """Add a connecting subgraph."""
        sources1, sources2 = itertools.tee(sources)
        targets1, targets2 = itertools.tee(targets)

        return self._graph_builder.add_connecting_subgraph(
            sources=sources1,
            targets=targets1,
            get_successors=self._graph.successors,
            get_no_connecting_subgraph_exception=lambda: NoConnectingSubgraphError(
                sources=sources2, targets=targets2
            ),
        )

    def add_component_subgraph(self, node: T) -> set[T]:
        """Add a component subgraph."""
        return self._graph_builder.add_component_subgraph(
            node,
            get_successors=self._graph.successors,
            get_predecessors=self._graph.predecessors,
        )

    def add_all(self) -> set[T]:
        """Add the whole graph."""
        for node in self._graph.nodes():
            self._graph_builder.add_node(node)

        for source, target in self._graph.edges():
            self._graph_builder.add_edge(source=source, target=target)

        return set(self._graph.nodes())

    def build(self) -> DirectedGraph[T]:
        return DirectedGraph(self._graph_builder.build().items())


class DirectedGraph[T: Hashable]:
    """Digraph with no parallel edges."""

    def __init__(
        self, connections: Iterable[tuple[T, Iterable[T]]] | None = None
    ) -> None:
        """Initialize digraph."""
        try:
            self._bidict = bd.BiDirectionalSetDict[T](connections)
        except bd.ValuesAreNotAlsoKeysError as e:
            raise TargetsAreNotNotAlsoSourceNodesError(e.values) from e

    def __bool__(self) -> bool:
        """Check if digraph is not empty."""
        return bool(self.nodes())

    def __eq__(self, other: object) -> bool:
        """Check if digraph is equal to other."""
        if not isinstance(other, DirectedGraph):
            return NotImplemented

        return self.nodes() == other.nodes() and self.edges() == other.edges()

    def __str__(self) -> str:
        """Return string representation of digraph."""
        return f"{{{', '.join(f'{node}: {{{", ".join(str(successor) for successor in self.successors(node))}}}' if self.successors(node) else str(node) for node in self.nodes())}}}"

    def __repr__(self) -> str:
        """Return string representation of digraph."""
        nodes_with_successors = (
            f"{node!r}: {{{', '.join(repr(successor) for successor in self.successors(node))}}}"
            for node in self.nodes()
        )
        return f"{self.__class__.__name__}({{{', '.join(nodes_with_successors)}}})"

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        return len(self.predecessors(node))

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        return len(self.successors(node))

    def degree(self, node: T, /) -> int:
        """Return number of edges to and from node."""
        return self.in_degree(node) + self.out_degree(node)

    def add_node(self, node: T, /) -> None:
        """Add node to digraph."""
        if node in self.nodes():
            raise NodeAlreadyExistsError(node=node)

        self._bidict.add(key=node)

    def validate_node_can_be_removed(self, node: T, /) -> None:
        """Validate that node can be removed from digraph."""
        if not self.is_isolated(node):
            raise HasNeighboursError(
                node=node,
                predecessors=self.predecessors(node),
                successors=self.successors(node),
            )

    def remove_node(self, node: T, /) -> None:
        """Remove node from digraph."""
        self.validate_node_can_be_removed(node)
        del self._bidict[node]

    def nodes(self) -> NodesView[T]:
        """Return view of digraph nodes."""
        return NodesView(self._bidict.keys())

    def validate_edge_can_be_added(self, source: T, target: T) -> None:
        """Validate that edge can be added to digraph."""
        if (source, target) in self.edges():
            raise EdgeAlreadyExistsError(source=source, target=target)

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to digraph."""
        self.validate_edge_can_be_added(source=source, target=target)
        self._bidict.add(key=source, value=target)

    def remove_edge(self, source: T, target: T) -> None:
        """Remove edge from digraph."""
        for node in [source, target]:
            if node not in self.nodes():
                raise NodeDoesNotExistError(node=node)

        if (source, target) not in self.edges():
            raise EdgeDoesNotExistError(source=source, target=target)

        self._bidict.remove(key=source, value=target)

    def edges(self) -> EdgesView[T]:
        """Return view of digraph edges."""
        return EdgesView(self._bidict)

    def successors(self, node: T, /) -> NodesView[T]:
        """Return successors of node."""
        try:
            return NodesView(self._bidict[node])
        except KeyError as e:
            raise NodeDoesNotExistError(node) from e

    def predecessors(self, node: T, /) -> NodesView[T]:
        """Return predecessors of node."""
        try:
            return NodesView(self._bidict.inverse[node])
        except KeyError as e:
            raise NodeDoesNotExistError(node) from e

    def descendants(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> Generator[T, None, None]:
        """Yeild the descendants of several nodes."""
        nodes1, nodes2 = itertools.tee(nodes)

        for node in nodes1:
            if node not in self.nodes():
                raise NodeDoesNotExistError(node=node)

        nodes_to_check = collections.deque(nodes2)
        nodes_checked = set[T]()

        while nodes_to_check:
            node = nodes_to_check.popleft()

            if node in nodes_checked:
                continue

            nodes_checked.add(node)
            yield node

            if stop_condition is not None and stop_condition(node):
                continue

            nodes_to_check.extend(self.successors(node))

    def descendants_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedGraph[T]:
        """Return the descendants subgraph of several nodes.

        Stop searching beyond a specific node if the stop condition is met.
        Includes the starting nodes.
        """
        builder = DirectedSubgraphBuilder[T](self)
        _ = builder.add_descendants_subgraph(nodes, stop_condition)
        return builder.build()

    def ancestors(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> Generator[T, None, None]:
        """Yeild the ancestors of several nodes."""
        nodes1, nodes2 = itertools.tee(nodes)

        for node in nodes1:
            if node not in self.nodes():
                raise NodeDoesNotExistError(node=node)

        nodes_to_check = collections.deque(nodes2)
        nodes_checked = set[T]()

        while nodes_to_check:
            node = nodes_to_check.popleft()

            if node in nodes_checked:
                continue

            nodes_checked.add(node)
            yield node

            if stop_condition is not None and stop_condition(node):
                continue

            nodes_to_check.extend(self.predecessors(node))

    def ancestors_subgraph(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> DirectedGraph[T]:
        """Return the ancestors subgraph of several nodes.

        Stop searching beyond a specific node if the stop condition is met.
        Includes the starting nodes.
        """
        builder = DirectedSubgraphBuilder[T](self)
        _ = builder.add_ancestors_subgraph(nodes, stop_condition)
        return builder.build()

    def component_subgraph(self, node: T) -> DirectedGraph[T]:
        """Return component subgraph containing node."""
        builder = DirectedSubgraphBuilder[T](self)
        _ = builder.add_component_subgraph(node)
        return builder.build()

    def component_subgraphs(self) -> Generator[DirectedGraph[T], None, None]:
        """Yield component subgraphs in the graph."""
        # TODO: Repeating this same code in every subclass. Find a way to DRY it out
        checked_nodes = set[T]()
        for node in self.nodes():
            if node in checked_nodes:
                continue

            component = self.component_subgraph(node)
            checked_nodes.update(component.nodes())
            yield component

    def connecting_subgraph(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> DirectedGraph[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        # TODO: Add stop condition parameter
        builder = DirectedSubgraphBuilder[T](self)
        _ = builder.add_connecting_subgraph(sources, targets)
        return builder.build()

    def is_root(self, node: T, /) -> bool:
        """Check if node is a root of the graph."""
        return not self.predecessors(node)

    def roots(self) -> Generator[T, None, None]:
        """Yield all roots of the graph."""
        for node in self.nodes():
            if self.is_root(node):
                yield node

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        return not self.successors(node)

    def leaves(self) -> Generator[T, None, None]:
        """Yield all leaves of the graph."""
        for node in self.nodes():
            if self.is_leaf(node):
                yield node

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        return self.is_leaf(node) and self.is_root(node)

    def isolated_nodes(self) -> Generator[T, None, None]:
        """Yield all isolated nodes."""
        for node in self.nodes():
            if self.is_isolated(node):
                yield node

    def has_loop(self) -> bool:
        """Check if the graph has a loop."""
        return any(node in self.successors(node) for node in self.nodes())

    def has_cycle(self) -> bool:
        """Check if the graph has a cycle."""

        def process_node(
            node: T, visited_nodes: set[T], current_subgraph_nodes: set[T]
        ) -> bool:
            visited_nodes.add(node)
            current_subgraph_nodes.add(node)

            for successor in self.successors(node):
                if successor in current_subgraph_nodes or (
                    successor not in visited_nodes
                    and process_node(successor, visited_nodes, current_subgraph_nodes)
                ):
                    return True

            current_subgraph_nodes.remove(node)
            return False

        visited_nodes = set[T]()
        current_subgraph_nodes = set[T]()
        return any(
            node not in visited_nodes
            and process_node(node, visited_nodes, current_subgraph_nodes)
            for node in self.nodes()
        )
