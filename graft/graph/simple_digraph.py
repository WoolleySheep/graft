"""DiGraph and associated Exceptions."""

import collections
from collections.abc import Hashable, Iterable, Iterator
from typing import Any, Generic, Self, TypeVar

from graft.graph import bidirectional_multidict

T = TypeVar("T", bound=Hashable)


class NodeAlreadyExistsError(Exception):
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


class NodeDoesNotExistError(Exception):
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


class HasEdgesError(Exception):
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


class EdgeAlreadyExistsError(Exception):
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


class EdgeDoesNotExistError(Exception):
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


class NoConnectingSubgraphError(Exception):
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


class SimpleDiGraph(Generic[T]):
    """Digraph with no loops or parallel edges."""

    def __init__(self) -> None:
        """Initialize SimpleDiGraph."""
        self._bidict = bidirectional_multidict.BiDirectionalMultiDict[T]()

    def __bool__(self) -> bool:
        """Check if digraph has any nodes."""
        return bool(self._bidict)

    def __contains__(self, node: T) -> bool:
        """Check if node exists in digraph."""
        return node in self._bidict

    def __iter__(self) -> Iterator[T]:
        """Return iterator over digraph nodes."""
        return iter(self._bidict)

    def __getitem__(self, node: T) -> Iterator[T]:
        """Return iterator over successors of node."""
        yield from self._bidict[node]

    def __str__(self) -> str:
        """Return string representation of digraph."""
        return str(self._bidict)

    def __repr__(self) -> str:
        """Return string representation of digraph."""
        return str(self._bidict)

    def __len__(self) -> int:
        """Return number of nodes in digraph."""
        return len(self._bidict)

    def in_degree(self, node: T, /) -> int:
        """Return number of incoming edges to node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return sum(1 for _ in self.predecessors(node))

    def out_degree(self, node: T, /) -> int:
        """Return number of outgoing edges from node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return sum(1 for _ in self.successors(node))

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
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        if not self.is_isolated(node):
            raise HasEdgesError(
                node=node,
                successors=self.successors(node),
                predecessors=self.predecessors(node),
            )

        del self._bidict[node]

    def nodes(self) -> Iterator[T]:
        """Return nodes of digraph."""
        return iter(self)

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to digraph."""
        if source == target:
            raise LoopError(node=source)

        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if self._has_edge(source=source, target=target):
            raise EdgeAlreadyExistsError(source=source, target=target)

        self._bidict.add(key=source, value=target)

    def remove_edge(self, source: T, target: T) -> None:
        """Remove edge from digraph."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if not self._has_edge(source=source, target=target):
            raise EdgeDoesNotExistError(source=source, target=target)

        self._bidict.remove(key=source, value=target)

    def edges(self) -> Iterator[tuple[T, T]]:
        """Return edges of digraph."""
        for source, targets in self._bidict.items():
            for target in targets:
                yield (source, target)

    def _has_edge(self, source: T, target: T) -> bool:
        """Check if edge exists in digraph."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return target in self.successors(source)

    def successors(self, node: T, /) -> Iterator[T]:
        """Return successors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._bidict[node]

    def has_successors(self, node: T, /) -> bool:
        """Check if node has any successors."""
        return bool(self.out_degree(node))

    def predecessors(self, node: T, /) -> Iterator[T]:
        """Return predecessors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._bidict.inverse[node]

    def has_predecessors(self, node: T, /) -> bool:
        """Check if node has any predecessors."""
        return bool(self.in_degree(node))

    def descendants_bfs(self, node: T, /) -> Iterator[T]:
        """Return breadth first search of descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = set[T]([node])
        queue = collections.deque[T](self.successors(node))

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.successors(node2))
            yield node2

    def descendants_dfs(self, node: T, /) -> Iterator[T]:
        """Return depth first search of the descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = set[T]([node])
        stack = collections.deque[T](self.successors(node))

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

    def ancestors_bfs(self, node: T, /) -> Iterator[T]:
        """Return breadth first search of ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = set[T]([node])
        queue = collections.deque[T](self.predecessors(node))

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.predecessors(node2))
            yield node2

    def ancestors_dfs(self, node: T, /) -> Iterator[T]:
        """Return depth first search of ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = set[T]([node])
        stack = collections.deque[T](self.predecessors(node))

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
        """Check if there is a path from source to target."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return target in self.descendants_bfs(source)

    def connecting_subgraph(self, source: T, target: T) -> Self:
        """Return connecting subgraph from source to target."""
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
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return not self.has_predecessors(node)

    def roots(self) -> Iterable[T]:
        """Return all roots of the graph."""
        for node in self:
            if self.is_root(node):
                yield node

    def is_leaf(self, node: T, /) -> bool:
        """Check if node is a leaf of the graph."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return not self.has_successors(node)

    def leaves(self) -> Iterable[T]:
        """Return all leaves of the graph."""
        for node in self:
            if self.is_leaf(node):
                yield node

    def is_isolated(self, node: T, /) -> bool:
        """Check if node is isolated."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        return not (self.has_predecessors(node) or self.has_successors(node))

    def isolated_nodes(self) -> Iterable[T]:
        """Return all isolated nodes."""
        for node in self:
            if self.is_isolated(node):
                yield node
