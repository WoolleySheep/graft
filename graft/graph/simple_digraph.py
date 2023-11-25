"""DiGraph and associated Exceptions."""

import collections
from collections.abc import (
    Generator,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    Set,
)
from typing import Any, Self, TypeGuard

from graft.graph import bidict

class NodeAlreadyExistsError[T: Hashable](Exception):
    """Raised when node already exists."""

    def __init__(
        self,
        node: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NodeAlreadyExistsError."""
        self.node = node
        super().__init__(f"node [{node}] already exists", *args, **kwargs)


class NodeDoesNotExistError[T: Hashable](Exception):
    """Raised when node does not exist."""

    def __init__(
        self,
        node: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NodeDoesNotExistError."""
        self.node = node
        super().__init__(f"node [{node}] does not exist", *args, **kwargs)


class HasEdgesError[T: Hashable](Exception):
    """Raised when node has edges."""

    def __init__(
        self,
        node: T,
        successors: Iterable[T],
        predecessors: Iterable[T],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize HasEdgesError."""
        self.node = node
        self.successors = set[T](successors)
        self.predecessors = set[T](predecessors)
        self.node = node
        super().__init__(f"node [{node}] has edges", *args, **kwargs)


class EdgeAlreadyExistsError[T: Hashable](Exception):
    """Raised when edge already exists."""

    def __init__(
        self,
        source: T,
        target: T,
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


class EdgeDoesNotExistError[T: Hashable](Exception):
    """Raised when edge does not exist."""

    def __init__(
        self,
        source: T,
        target: T,
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


class LoopError[T: Hashable](Exception):
    """Loop error.

    Raised when an edge is referenced that connects a node to itself, creating a
    loop. These aren't allowed in simple digraphs.
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


class NoConnectingSubgraphError[T: Hashable](Exception):
    """Raised when no connecting subgraph exists."""

    def __init__(
        self,
        source: T,
        target: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NoConnectingSubgraphError."""
        self.source = source
        self.target = target
        super().__init__(
            f"no connecting subgraph from [{source}] to [{target}] exists",
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
        """Check if item is in NodeView."""
        return item in self._nodes

    def __iter__(self) -> Iterator[T]:
        """Return iterator over nodes in view."""
        return iter(self._nodes)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"nodes_view({{{', '.join(str(node) for node in self._nodes)}}})"


class EdgesView[T: Hashable](Set[tuple[T, T]]):
    """View of a set of edges."""

    def __init__(self, node_successors_map: Mapping[T, Set[T]], /) -> None:
        """Initialise EdgesView."""
        self._node_successors_map: Mapping[T, Set[T]] = node_successors_map

    def __bool__(self) -> bool:
        """Check view has any edges."""
        return any(self._node_successors_map.values())

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
            if not isinstance(item, tuple):
                return False

            if len(item) != 2:
                return False

            return all(isinstance(element, Hashable) for element in item)

        if not is_two_element_tuple_of_hashables(item):
            raise TypeError

        source, target = item

        if source == target:
            raise LoopError(node=source)

        for node in [source, target]:
            if node not in self._node_successors_map:
                raise NodeDoesNotExistError(node)

        return target in self._node_successors_map[source]

    def __iter__(self) -> Generator[tuple[T, T], None, None]:
        """Return generator over edges in view."""
        for node, successors in self._node_successors_map.items():
            for successor in successors:
                yield (node, successor)

    def __str__(self) -> str:
        """Return string representation of view."""
        node_with_successors = list[str]()
        for node, successors in self._node_successors_map.items():
            node_with_successors.append(
                ", ".join(f"({node}, {successor})" for successor in successors),
            )
        return f"edges_view({{{', '.join(node_with_successors)}}})"


class SimpleDiGraph[T: Hashable]:
    """Digraph with no loops or parallel edges."""

    def __init__(self) -> None:
        """Initialize simple digraph."""
        self._bidict = bidict.BiDirectionalSetValueDict[T]()

    def __bool__(self) -> bool:
        """Check if digraph has any nodes."""
        return bool(self.nodes())

    def __contains__(self, item: object) -> bool:
        """Check if item is a node in digraph."""
        return item in self.nodes()

    def __iter__(self) -> Iterator[T]:
        """Return iterator over digraph nodes."""
        return iter(self.nodes())

    def __str__(self) -> str:
        """Return string representation of digraph."""
        nodes_with_successors = list[str]()
        for node, successors in self._bidict.items():
            nodes_with_successors.append(
                f"{node}: {{{', '.join(str(value) for value in successors)}}}",
            )
        return f"simple_digraph({{{', '.join(nodes_with_successors)}}})"

    def __len__(self) -> int:
        """Return number of nodes in digraph."""
        return len(self.nodes())

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
        if node in self:
            raise NodeAlreadyExistsError(node=node)

        self._bidict.add(key=node)

    def remove_node(self, node: T, /) -> None:
        """Remove node from digraph."""
        if not self.is_isolated(node):
            raise HasEdgesError(
                node=node,
                successors=self.successors(node),
                predecessors=self.predecessors(node),
            )

        del self._bidict[node]

    def nodes(self) -> NodesView[T]:
        """Return view of digraph nodes."""
        return NodesView(self._bidict.keys())

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to digraph."""
        if (source, target) in self.edges():
            raise EdgeAlreadyExistsError(source=source, target=target)

        self._bidict.add(key=source, value=target)

    def remove_edge(self, source: T, target: T) -> None:
        """Remove edge from digraph."""
        if (source, target) not in self.edges():
            raise EdgeDoesNotExistError(source=source, target=target)

        self._bidict.remove(key=source, value=target)

    def edges(self) -> EdgesView[T]:
        """Return view of digraph edges."""
        return EdgesView(self._bidict)

    def successors(self, node: T, /) -> NodesView[T]:
        """Return successors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict[node])

    def predecessors(self, node: T, /) -> NodesView[T]:
        """Return predecessors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return NodesView(self._bidict.inverse[node])

    def descendants_bfs(self, node: T, /) -> Generator[T, None, None]:
        """Return breadth first search of descendants of node."""
        queue = collections.deque[T](self.successors(node))
        visited = set[T]([node])

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.successors(node2))
            yield node2

    def descendants_dfs(self, node: T, /) -> Generator[T, None, None]:
        """Return depth first search of the descendants of node."""
        stack = collections.deque[T](self.successors(node))
        visited = set[T]([node])

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.successors(node2))
            yield node2

    def descendants_subgraph(self, node: T, /) -> Self:
        """Return a subgraph of the descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        subgraph = type(self)()
        subgraph.add_node(node)

        visited = set[T]()
        queue = collections.deque[T]([node])

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            for successor in self.successors(node2):
                if successor not in subgraph:
                    subgraph.add_node(successor)
                subgraph.add_edge(node2, successor)
                queue.append(successor)

        return subgraph

    def ancestors_bfs(self, node: T, /) -> Generator[T, None, None]:
        """Return breadth first search of ancestors of node."""
        queue = collections.deque[T](self.predecessors(node))
        visited = set[T]([node])

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.predecessors(node2))
            yield node2

    def ancestors_dfs(self, node: T, /) -> Generator[T, None, None]:
        """Return depth first search of ancestors of node."""
        stack = collections.deque[T](self.predecessors(node))
        visited = set[T]([node])

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.predecessors(node2))
            yield node2

    def ancestors_subgraph(self, node: T, /) -> Self:
        """Return a subgraph of the ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        subgraph = type(self)()
        subgraph.add_node(node)

        visited = set[T]()
        queue = collections.deque[T]([node])

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            for predecessor in self.predecessors(node2):
                if predecessor not in subgraph:
                    subgraph.add_node(predecessor)
                subgraph.add_edge(predecessor, node2)
                queue.append(predecessor)

        return subgraph

    def has_path(self, source: T, target: T) -> bool:
        """Check if there's a connecting subgraph/path from source to target."""
        if source == target:
            raise LoopError(node=source)

        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return target in self.descendants_bfs(source)

    def connecting_subgraph(self, source: T, target: T) -> Self:
        """Return connecting subgraph from source to target."""
        if source == target:
            raise LoopError(node=source)

        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        source_descendants_subgraph = self.descendants_subgraph(source)
        try:
            return source_descendants_subgraph.ancestors_subgraph(target)
        except NodeDoesNotExistError as e:
            raise NoConnectingSubgraphError(source=source, target=target) from e

    def is_root(self, node: T, /) -> bool:
        """Check if node is a root of the graph."""
        return not self.predecessors(node)

    def roots(self) -> Generator[T, None, None]:
        """Yield all roots of the graph."""
        for node in self:
            if self.is_root(node):
                yield node

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        return not self.successors(node)

    def leaves(self) -> Generator[T, None, None]:
        """Yield all leaves of the graph."""
        for node in self:
            if self.is_leaf(node):
                yield node

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        return not (self.successors(node) or self.predecessors(node))

    def isolated_nodes(self) -> Generator[T, None, None]:
        """Yield all isolated nodes."""
        for node in self:
            if self.is_isolated(node):
                yield node
