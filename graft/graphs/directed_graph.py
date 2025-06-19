"""Simple DiGraph and associated Exceptions."""

from __future__ import annotations

import collections
import enum
import itertools
from collections.abc import (
    Callable,
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Set,
)
from typing import Any, TypeGuard

from graft.graphs import bidict as bd


class TraversalOrder(enum.Enum):
    DEPTH_FIRST = enum.auto()
    BREADTH_FIRST = enum.auto()


class SubgraphType(enum.Enum):
    """Used with subgraph edges view."""

    ANCESTORS = enum.auto()
    DESCENDANTS = enum.auto()


def _traverse[T: Hashable](
    node: T,
    node_neighbours_map: Mapping[T, Set[T]],
    order: TraversalOrder,
    stop_condition: Callable[[T], bool] | None = None,
) -> Generator[T, None, None]:
    """Traverse the graph from a given node, following the given traversal order.

    Stop traversing beyond a specific node if the stop condition is met.

    The starting node is not included in the yielded nodes, but it is checked
    against the stop condition.

    Extracted out into its own function due to the commonalities between
    DFS/BFS and descendants/ancestors.
    """
    if node not in node_neighbours_map:
        raise NodeDoesNotExistError(node)

    if stop_condition is not None and stop_condition(node):
        return

    visited_nodes = set[T]([node])
    nodes_to_check = collections.deque[T](node_neighbours_map[node])

    match order:
        case TraversalOrder.DEPTH_FIRST:
            pop_next_node = nodes_to_check.pop  # Stack
        case TraversalOrder.BREADTH_FIRST:
            pop_next_node = nodes_to_check.popleft  # Queue

    while nodes_to_check:
        node2 = pop_next_node()
        if node2 in visited_nodes:
            continue
        visited_nodes.add(node2)
        yield node2
        if stop_condition is not None and stop_condition(node2):
            continue
        nodes_to_check.extend(node_neighbours_map[node2])


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


class HasPredecessorsError(Exception):
    """Raised when a task has predecessors."""

    def __init__(self, node: Hashable, predecessors: Iterable[Any]) -> None:
        """Initialise HasPredecessorsError."""
        self.node = node
        self.predecessors = set(predecessors)
        formatted_predecessors = (str(predecessor) for predecessor in predecessors)
        super().__init__(
            f"Node [{node}] has predecessors [{', '.join(formatted_predecessors)}]"
        )


class HasSuccessorsError(Exception):
    """Raised when a task has successors."""

    def __init__(self, node: Hashable, successors: Iterable[Any]) -> None:
        """Initialise HasSuccessorsError."""
        self.node = node
        self.successors = set(successors)
        formatted_successors = (str(successor) for successor in successors)
        super().__init__(
            f"Node [{node}] has successors [{', '.join(formatted_successors)}]"
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
        return isinstance(other, NodesView) and set(self) == set(other)

    def __str__(self) -> str:
        """Return string representation of the nodes."""
        return f"{{{', '.join(str(node) for node in self)}}}"

    def __repr__(self) -> str:
        """Return string representation of the nodes."""
        return f"{self.__class__.__name__}{{{', '.join(repr(node) for node in self)}}}"

    def __sub__(self, other: Set[Any]) -> NodesView[T]:
        """Return difference of two views."""
        return NodesView(self._nodes - other)

    def __and__(self, other: Set[Any]) -> NodesView[T]:
        """Return intersection of two views."""
        return NodesView(self._nodes & other)

    def __or__(self, other: Set[T]) -> NodesView[T]:
        """Return union of two views."""
        return NodesView(self._nodes | other)

    def __xor__(self, other: Set[T]) -> NodesView[T]:
        """Return symmetric difference of two views."""
        return NodesView(self._nodes ^ other)


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
        return isinstance(other, EdgesView) and set(self) == set(other)

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
            raise TypeError

        source, target = item

        return (
            source in self._node_successors_map
            and target in self._node_successors_map[source]
        )

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

    def __sub__(self, other: Set[Any]) -> EdgesView[T]:
        """Return difference of two views."""
        difference = dict[T, set[T]]()
        for source, target in self:
            if (source, target) in other:
                continue
            if source not in difference:
                difference[source] = set[T]()
            difference[source].add(target)

        return EdgesView(difference)

    def __and__(self, other: Set[Any]) -> EdgesView[T]:
        """Return intersection of two views."""
        intersection = dict[T, set[T]]()
        for source, target in self:
            if (source, target) not in other:
                continue
            if source not in intersection:
                intersection[source] = set[T]()
            intersection[source].add(target)

        return EdgesView(intersection)

    def __or__(self, other: Set[tuple[T, T]]) -> EdgesView[T]:
        """Return union of two views."""
        union = {
            source: set(targets)
            for source, targets in self._node_successors_map.items()
        }
        for source, target in other:
            if source not in union:
                union[source] = set[T]()
            union[source].add(target)

        return EdgesView(union)

    def __xor__(self, other: Set[tuple[T, T]]) -> EdgesView[T]:
        """Return symmetric difference of two views."""
        intersection = self & other
        symmetric_difference = dict[T, set[T]]()
        for source, target in itertools.chain(self, other):
            if (source, target) in intersection:
                continue
            if source not in symmetric_difference:
                symmetric_difference[source] = set[T]()
            symmetric_difference[source].add(target)

        return EdgesView(symmetric_difference)


class SubgraphNodesView[T: Hashable](Set[T]):
    """View of the nodes in the subgraph."""

    def __init__(
        self,
        starting_nodes: Iterable[T],
        node_neighbours_map: Mapping[T, Set[T]],
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        self._starting_nodes = set(starting_nodes)

        if not self._starting_nodes:
            # TODO: Add proper exception
            msg = "starting nodes cannot be empty"
            raise ValueError(msg)

        for node in self._starting_nodes:
            if node not in node_neighbours_map:
                raise NodeDoesNotExistError(node)

        self._node_neighbours_map = node_neighbours_map
        self._stop_condition = stop_condition

    def __bool__(self) -> bool:
        """Check if any nodes in the subgraph."""
        return any(
            (self._stop_condition is None or not self._stop_condition(node))
            and self._node_neighbours_map[node] > self._starting_nodes
            for node in self._starting_nodes
        )

    def __eq__(self, other: object) -> bool:
        """Check if subgraph nodes view is equal to other."""
        return isinstance(other, SubgraphNodesView) and set(self) == set(other)

    def __contains__(self, item: object) -> bool:
        """Check if item is a node in the subgraph."""
        if item in self._starting_nodes:
            return False

        visited_nodes = set[T]()
        nodes_to_check = collections.deque(self._starting_nodes)

        while nodes_to_check:
            node = nodes_to_check.popleft()

            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            if self._stop_condition is not None and self._stop_condition(node):
                continue

            if item in self._node_neighbours_map[node]:
                return True

            nodes_to_check.extend(self._node_neighbours_map[node])

        return False

    def __len__(self) -> int:
        """Return number of nodes in the subgraph."""
        return sum(1 for _ in self)

    def __iter__(self) -> Generator[T, None, None]:
        """Return generator over nodes in the subgraph."""
        visited_nodes = set[T](self._starting_nodes)

        nodes_to_check = collections.deque[T]()
        for node in self._starting_nodes:
            if self._stop_condition is not None and self._stop_condition(node):
                continue
            nodes_to_check.extend(self._node_neighbours_map[node])

        while nodes_to_check:
            node = nodes_to_check.popleft()

            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            yield node

            if self._stop_condition is not None and self._stop_condition(node):
                continue

            nodes_to_check.extend(self._node_neighbours_map[node])

    def contains(self, nodes: Iterable[T]) -> Generator[bool, None, None]:
        """Check if nodes are in the subgraph.

        Theoretically faster than checking if the subgraph contains multiple nodes
        one at a time, as can cache the parts of the subgraph already searched.
        """

        def contains_recursive(
            node: T,
            nodes_in_subgraph: set[T],
            visited_nodes: set[T],
            nodes_to_check: collections.deque[T],
        ) -> bool:
            if node not in self._node_neighbours_map:
                return False

            if node in self._starting_nodes:
                return False

            if node in nodes_in_subgraph:
                return True

            while nodes_to_check:
                node2 = nodes_to_check.popleft()

                if node2 in visited_nodes:
                    continue
                visited_nodes.add(node2)

                if self._stop_condition is not None and self._stop_condition(node2):
                    continue

                nodes_to_check.extend(self._node_neighbours_map[node2])
                nodes_in_subgraph.update(self._node_neighbours_map[node2])

                if node in self._node_neighbours_map[node2]:
                    return True

            return False

        nodes_in_subgraph = set[T]()
        visited_nodes = set[T]()
        nodes_to_check = collections.deque[T](self._starting_nodes)

        for node in nodes:
            yield contains_recursive(
                node, nodes_in_subgraph, visited_nodes, nodes_to_check
            )

    def __sub__(self, other: Set[Any]) -> SubgraphNodesView[T]:
        """Return difference of two views."""
        raise NotImplementedError

    def __and__(self, other: Set[Any]) -> SubgraphNodesView[T]:
        """Return intersection of two views."""
        raise NotImplementedError

    def __or__(self, other: Set[T]) -> SubgraphNodesView[T]:
        """Return union of two views."""
        raise NotImplementedError

    def __xor__(self, other: Set[T]) -> SubgraphNodesView[T]:
        """Return symmetric difference of two views."""
        raise NotImplementedError


class SubgraphEdgesView[T: Hashable](Set[tuple[T, T]]):
    """View of the edges in the subgraph."""

    def __init__(
        self,
        starting_nodes: Iterable[T],
        node_neighbours_map: Mapping[T, Set[T]],
        subgraph_type: SubgraphType,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        self._starting_nodes = set(starting_nodes)

        if not self._starting_nodes:
            # TODO: Add proper exception
            msg = "starting nodes cannot be empty"
            raise ValueError(msg)

        for node in self._starting_nodes:
            if node not in node_neighbours_map:
                raise NodeDoesNotExistError(node)

        self._node_neighbours_map = node_neighbours_map
        self._subgraph_type = subgraph_type
        self._stop_condition = stop_condition

    def __bool__(self) -> bool:
        """Check if any edges in the subgraph."""
        return any(
            (self._stop_condition is None or not self._stop_condition(node))
            and self._node_neighbours_map[node] > self._starting_nodes
            for node in self._starting_nodes
        )

    def __eq__(self, other: object) -> bool:
        """Check if subgraph nodes view is equal to other."""
        return isinstance(other, SubgraphNodesView) and set(self) == set(other)

    def __contains__(self, item: object) -> bool:
        """Check if item is an edge in the subgraph.

        Note that this method will return false if either of the nodes
        is not present in the graph. It could be argued this should throw a
        TaskNotExist exception. Not sure yet.
        """
        # TODO: This is confusing, and I wrote it. Simplify if possible.

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
            raise TypeError

        for node in item:
            if node not in self._node_neighbours_map:
                return False

        match self._subgraph_type:
            case SubgraphType.DESCENDANTS:
                node, neighbour = item
            case SubgraphType.ANCESTORS:
                neighbour, node = item

        visited_nodes = set[T]()
        nodes_to_check = collections.deque(self._starting_nodes)

        while nodes_to_check:
            node2 = nodes_to_check.popleft()

            if node2 in visited_nodes:
                continue
            visited_nodes.add(node2)

            if node2 == node:
                return (
                    self._stop_condition is None or not self._stop_condition(node2)
                ) and neighbour in self._node_neighbours_map[node]

            nodes_to_check.extend(self._node_neighbours_map[node])

        return False

    def __iter__(self) -> Generator[tuple[T, T]]:
        """Return generator over edges in the subgraph."""
        visited_nodes = set[T]()
        nodes_to_check = collections.deque[T](self._starting_nodes)

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            if self._stop_condition is not None and self._stop_condition(node):
                continue

            for neighbour in self._node_neighbours_map[node]:
                match self._subgraph_type:
                    case SubgraphType.DESCENDANTS:
                        yield (node, neighbour)
                    case SubgraphType.ANCESTORS:
                        yield (neighbour, node)

                nodes_to_check.append(neighbour)

    def __len__(self) -> int:
        """Return number of edges in the subgraph."""
        return sum(1 for _ in self)

    def contains(self, edges: Iterable[tuple[T, T]]) -> Generator[bool, None, None]:
        """Check if edges are in the subgraph.

        Theoretically faster than checking if the subgraph contains multiple edges
        one at a time, as can cache the parts of the subgraph already searched.
        """

        def contains_recursive(
            edge: tuple[T, T],
            node_neighbours_in_subgraph: dict[T, set[T]],
            visited_nodes: set[T],
            nodes_to_check: collections.deque[T],
        ) -> bool:
            source, target = edge
            if source not in self._node_neighbours_map:
                return False

            if source in node_neighbours_in_subgraph:
                return target in node_neighbours_in_subgraph[source]

            while nodes_to_check:
                node = nodes_to_check.popleft()

                if node in visited_nodes:
                    continue
                visited_nodes.add(node)

                neighbours = (
                    set(self._node_neighbours_map[node])
                    if self._stop_condition is None or self._stop_condition(node)
                    else set[T]()
                )
                node_neighbours_in_subgraph[node] = neighbours
                nodes_to_check.extend(neighbours)

                if node == source:
                    return target in neighbours

            return False

        node_neighbours_in_subgraph = dict[T, set[T]]()
        visited_nodes = set[T]()
        nodes_to_check = collections.deque[T](self._starting_nodes)

        for edge in edges:
            yield contains_recursive(
                edge, node_neighbours_in_subgraph, visited_nodes, nodes_to_check
            )

    def __sub__(self, other: Set[Any]) -> SubgraphEdgesView[T]:
        """Return difference of two views."""
        raise NotImplementedError

    def __and__(self, other: Set[Any]) -> SubgraphEdgesView[T]:
        """Return intersection of two views."""
        raise NotImplementedError

    def __or__(self, other: Set[tuple[T, T]]) -> SubgraphEdgesView[T]:
        """Return union of two views."""
        raise NotImplementedError

    def __xor__(self, other: Set[tuple[T, T]]) -> SubgraphEdgesView[T]:
        """Return symmetric difference of two views."""
        raise NotImplementedError


class MultipleStartingNodesSubgraphView[T: Hashable]:
    """View of a subgraph with multiple starting nodes."""

    def __init__(
        self,
        starting_nodes: Iterable[T],
        node_successors_map: bd.BiDirectionalSetDict[T],
        subgraph_type: SubgraphType,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        self._starting_nodes = set(starting_nodes)

        if not self._starting_nodes:
            # TODO: Add proper exception
            msg = "starting nodes cannot be empty"
            raise ValueError(msg)

        for node in self._starting_nodes:
            if node not in node_successors_map:
                raise NodeDoesNotExistError(node)

        match subgraph_type:
            case SubgraphType.DESCENDANTS:
                self._node_neighbours_map = node_successors_map
            case SubgraphType.ANCESTORS:
                self._node_neighbours_map = node_successors_map.inverse

        self._subgraph_type = subgraph_type
        self._stop_condition = stop_condition

    def __bool__(self) -> bool:
        """Check if subgraph is not empty."""
        return bool(self.edges())

    def __eq__(self, other: object) -> bool:
        """Check if subgraph view is equal to other."""
        return (
            isinstance(other, MultipleStartingNodesSubgraphView)
            and self.nodes() == other.nodes()
            and self.edges() == other.edges()
        )

    def nodes(self) -> SubgraphNodesView[T]:
        """Return view of the nodes."""
        return SubgraphNodesView(
            self._starting_nodes, self._node_neighbours_map, self._stop_condition
        )

    def edges(self) -> SubgraphEdgesView[T]:
        """Return view of the edges."""
        return SubgraphEdgesView(
            self._starting_nodes,
            self._node_neighbours_map,
            self._subgraph_type,
            self._stop_condition,
        )

    def _populate_graph(
        self,
        graph: DirectedGraph[T],
    ) -> None:
        """Populate a graph with the subgraph of the starting nodes.

        Note that the starting nodes will be included.

        Only meant to be called by subgraph to facilitate easy subclassing.

        Be aware that if an exception is raised, the graph may be partially
        populated.
        """
        for node in self._starting_nodes:
            if node not in graph.nodes():
                graph.add_node(node)

        visited_nodes = set[T]()
        nodes_to_check = collections.deque[T](self._starting_nodes)

        while nodes_to_check:
            node = nodes_to_check.pop()

            if node in visited_nodes:
                continue
            visited_nodes.add(node)

            if self._stop_condition and self._stop_condition(node):
                continue

            for neighbour in self._node_neighbours_map[node]:
                if neighbour not in graph.nodes():
                    graph.add_node(neighbour)

                match self._subgraph_type:
                    case SubgraphType.DESCENDANTS:
                        source, target = node, neighbour
                    case SubgraphType.ANCESTORS:
                        source, target = neighbour, node

                if (source, target) not in graph.edges():
                    graph.add_edge(source, target)

                nodes_to_check.append(neighbour)

    def subgraph(self) -> DirectedGraph[T]:
        """Return subgraph of the descendants of the node.

        Note that the starting nodes will be included.
        """
        subgraph = DirectedGraph[T]()
        self._populate_graph(graph=subgraph)
        return subgraph


class SingleStartingNodeSubgraphView[T: Hashable](MultipleStartingNodesSubgraphView[T]):
    """View of a subgraph with a single starting node."""

    def __init__(
        self,
        starting_node: T,
        node_successors_map: bd.BiDirectionalSetDict[T],
        subgraph_type: SubgraphType,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> None:
        if starting_node not in node_successors_map:
            raise NodeDoesNotExistError(starting_node)

        # Can reuse the methods in the multiple starting nodes version if we
        # store the node in the starting nodes set
        self._starting_nodes = set[T]([starting_node])

        match subgraph_type:
            case SubgraphType.DESCENDANTS:
                self._node_neighbours_map = node_successors_map
            case SubgraphType.ANCESTORS:
                self._node_neighbours_map = node_successors_map.inverse

        self._subgraph_type = subgraph_type
        self._stop_condition = stop_condition

    def traverse(
        self, order: TraversalOrder = TraversalOrder.BREADTH_FIRST
    ) -> Generator[T, None, None]:
        """Return generator that traverses nodes in view in order.

        Starts from the starting node, but does not include it.
        """
        assert len(self._starting_nodes) == 1

        return _traverse(
            node=next(iter(self._starting_nodes)),
            node_neighbours_map=self._node_neighbours_map,
            order=order,
            stop_condition=self._stop_condition,
        )


class DirectedGraph[T: Hashable]:
    """Digraph with no parallel edges."""

    def __init__(self, bidict: bd.BiDirectionalSetDict[T] | None = None) -> None:
        """Initialize digraph."""
        self._bidict = bidict or bd.BiDirectionalSetDict[T]()

    def __bool__(self) -> bool:
        """Check if digraph is not empty."""
        return bool(self.nodes())

    def __eq__(self, other: object) -> bool:
        """Check if digraph is equal to other."""
        return (
            isinstance(other, DirectedGraph)
            and self.nodes() == other.nodes()
            and self.edges() == other.edges()
        )

    def __str__(self) -> str:
        """Return string representation of digraph."""
        return str(self._bidict)

    def __repr__(self) -> str:
        """Return string representation of digraph."""
        nodes_with_successors = (
            f"{node!r}: {{{', '.join(repr(successor) for successor in successors)}}}"
            for node, successors in self.node_successors_pairs()
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
        if predecessors := self.predecessors(node):
            raise HasPredecessorsError(node=node, predecessors=predecessors)

        if successors := self.successors(node):
            raise HasSuccessorsError(node=node, successors=successors)

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
        if node not in self.nodes():
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict[node])

    def predecessors(self, node: T, /) -> NodesView[T]:
        """Return predecessors of node."""
        if node not in self.nodes():
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict.inverse[node])

    def descendants(
        self,
        node: T,
        /,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> SingleStartingNodeSubgraphView[T]:
        """Descendants of node.

        Stop searching beyond a specific node if the stop condition is met.
        """
        return SingleStartingNodeSubgraphView(
            node, self._bidict, SubgraphType.DESCENDANTS, stop_condition
        )

    def descendants_multi(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> MultipleStartingNodesSubgraphView[T]:
        """Descendants of several nodes.

        Stop searching beyond a specific node if the stop condition is met.
        """
        return MultipleStartingNodesSubgraphView(
            nodes, self._bidict, SubgraphType.DESCENDANTS, stop_condition
        )

    def ancestors(
        self,
        node: T,
        /,
        stop_condition: Callable[[T], bool] | None = None,
    ) -> SingleStartingNodeSubgraphView[T]:
        """Ancestors of node.

        Stop searching beyond a specific node if the stop condition is met.
        """
        return SingleStartingNodeSubgraphView(
            node, self._bidict, SubgraphType.ANCESTORS, stop_condition
        )

    def ancestors_multi(
        self, nodes: Iterable[T], /, stop_condition: Callable[[T], bool] | None = None
    ) -> MultipleStartingNodesSubgraphView[T]:
        """Ancestors of several nodes.

        Stop searching beyond a specific node if the stop condition is met.
        """
        return MultipleStartingNodesSubgraphView(
            nodes, self._bidict, SubgraphType.ANCESTORS, stop_condition
        )

    def has_path(
        self, source: T, target: T, stop_condition: Callable[[T], bool] | None = None
    ) -> bool:
        """Check if there's a connecting subgraph/path from source to target.

        If the source and target are the same (and exist), will return True.
        """
        for node in [source, target]:
            if node not in self.nodes():
                raise NodeDoesNotExistError(node=node)

        return (
            source == target
            or target in self.descendants(source, stop_condition=stop_condition).nodes()
        )

    def connecting_subgraph(self, source: T, target: T) -> DirectedGraph[T]:
        """Return connecting subgraph from source to target."""
        # TODO: Add stop condition parameter
        return self.connecting_subgraph_multi([source], [target])

    def component(self, node: T) -> DirectedGraph[T]:
        """Return component containing node."""
        subgraph = DirectedGraph[T]()
        self._populate_graph_with_component(graph=subgraph, node=node)
        return subgraph

    def _populate_graph_with_component(self, graph: DirectedGraph[T], node: T) -> None:
        """Populate a graph with the component containing the node.

        Only meant to be called by component to facilitate easy subclassing.

        Be aware that if an exception is raised, the graph may be partially
        populated.
        """
        # TODO: Make this function more efficient - it feels rubbish
        if node not in self.nodes():
            raise NodeDoesNotExistError(node=node)

        checked_nodes = set[T]()
        nodes_to_check = collections.deque([node])

        while nodes_to_check:
            node = nodes_to_check.popleft()

            if node in checked_nodes:
                continue
            checked_nodes.add(node)

            if node not in graph.nodes():
                graph.add_node(node)

            for predecessor in self.predecessors(node):
                if predecessor not in graph.nodes():
                    graph.add_node(predecessor)

                if (predecessor, node) not in graph.edges():
                    graph.add_edge(predecessor, node)

                nodes_to_check.append(predecessor)

            for successor in self.successors(node):
                if successor not in graph.nodes():
                    graph.add_node(successor)

                if (node, successor) not in graph.edges():
                    graph.add_edge(node, successor)

                nodes_to_check.append(successor)

    def components(self) -> Generator[DirectedGraph[T], None, None]:
        """Yield components in the graph."""
        components = list[DirectedGraph[T]]()
        for node in self.nodes():
            if any(node in component.nodes() for component in components):
                continue

            component = self.component(node)
            yield component
            components.append(component)

    def connecting_subgraph_multi(
        self, sources: Iterable[T], targets: Iterable[T]
    ) -> DirectedGraph[T]:
        """Return connecting subgraph from sources to targets.

        Every target must be reachable by one or more sources.
        """
        # TODO: Add stop condition parameter
        subgraph = DirectedGraph[T]()
        self._populate_graph_with_connecting(
            graph=subgraph, sources=sources, targets=targets
        )
        return subgraph

    def _populate_graph_with_connecting(
        self,
        graph: DirectedGraph[T],
        sources: Iterable[T],
        targets: Iterable[T],
    ) -> None:
        """Populate a graph with the subgraph connecting sources to targets.

        Only meant to be called by connecting_subgraph and
        connecting_subgraph_multi to facilitate easy subclassing. Be aware that
        if an exception is raised, the graph may be partially populated.
        """
        # TODO: Add stop condition parameter
        sources2 = list(sources)
        targets2 = list(targets)

        for node in itertools.chain(sources2, targets2):
            if node not in self.nodes():
                raise NodeDoesNotExistError(node=node)

        sources_descendants_subgraph = self.descendants_multi(sources2).subgraph()
        try:
            connecting_subgraph = sources_descendants_subgraph.ancestors_multi(
                targets2
            ).subgraph()
        except NodeDoesNotExistError as e:
            raise NoConnectingSubgraphError(sources=sources2, targets=targets2) from e

        graph.update(connecting_subgraph)

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

    def node_successors_pairs(
        self,
    ) -> Generator[tuple[T, NodesView[T]], None, None]:
        """Yield all node-successors pairs."""
        for node in self.nodes():
            yield node, self.successors(node)

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

    def update(self, graph: DirectedGraph[T]) -> None:
        """Update the graph with another graph.

        Use this method with caution; the order in which nodes and edges are
        added cannot be controlled, and they graph you're updating from may have
        edges that are not allowed in the graph you're updating. As such, I
        recommend only using it as a helper method when you know it won't fail.
        """
        for node in graph.nodes():
            if node in self.nodes():
                continue
            self.add_node(node)

        for source, target in graph.edges():
            if (source, target) in self.edges():
                continue
            self.add_edge(source, target)
