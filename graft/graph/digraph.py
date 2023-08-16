"""DiGraph and associated Exceptions."""

import collections
from collections.abc import Hashable, Iterable, Iterator
from typing import Any, Generic, Self, TypeVar

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
        self.successors = set(successors)
        self.predecessors = set(predecessors)
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


class DiGraph(Generic[T]):
    """Class for Directed Graph."""

    def __init__(self) -> None:
        """Initialize DiGraph."""
        self._successors: dict[T, set[T]] = {}
        self._predecessors: dict[T, set[T]] = {}

    def __bool__(self) -> bool:
        """Check if DiGraph has nodes."""
        return bool(self._successors)

    def __contains__(self, node: T) -> bool:
        """Check if node exists in DiGraph."""
        return node in self._successors

    def __iter__(self) -> Iterator[T]:
        """Return iterator of DiGraph."""
        return iter(self._successors)

    def __str__(self) -> str:
        """Return string representation of DiGraph."""
        return str(self._successors)

    def add_node(self, node: T, /) -> None:
        """Add node to DiGraph."""
        if node in self:
            raise NodeAlreadyExistsError(node=node)

        self._successors[node] = set()
        self._predecessors[node] = set()

    def remove_node(self, node: T, /) -> None:
        """Remove node from DiGraph."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        if self._successors[node] or self._predecessors[node]:
            raise HasEdgesError(
                node=node,
                successors=self._successors[node],
                predecessors=self._predecessors[node],
            )

        del self._successors[node]
        del self._predecessors[node]

    def nodes(self) -> Iterator[T]:
        """Return nodes of DiGraph."""
        return iter(self)

    def add_edge(self, source: T, target: T) -> None:
        """Add edge to DiGraph."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if target in self._successors[source]:
            raise EdgeAlreadyExistsError(source=source, target=target)

        self._successors[source].add(target)
        self._predecessors[target].add(source)

    def remove_edge(self, source: T, target: T) -> None:
        """Remove edge from DiGraph."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        if target not in self._successors[source]:
            raise EdgeDoesNotExistError(source=source, target=target)

        self._successors[source].remove(target)
        self._predecessors[target].remove(source)

    def edges(self) -> Iterator[tuple[T, T]]:
        """Return edges of DiGraph."""
        for source, targets in self._successors.items():
            for target in targets:
                yield (source, target)

    def _has_edge(self, source: T, target: T) -> bool:
        """Check if edge exists in DiGraph."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return target in self._successors[source]

    def successors(self, node: T, /) -> Iterator[T]:
        """Return successors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._successors[node]

    def has_successor(self, node: T, successor: T) -> bool:
        """Check if node has successor."""
        return self._has_edge(source=node, target=successor)

    def has_successors(self, node: T, /) -> bool:
        """Check if node has any successors."""
        return bool(self._successors[node])

    def predecessors(self, node: T, /) -> Iterator[T]:
        """Return predecessors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._predecessors[node]

    def has_predecessor(self, node: T, predecessor: T) -> bool:
        """Check if node has predecessor."""
        return self._has_edge(source=predecessor, target=node)

    def has_predecessors(self, node: T, /) -> bool:
        """Check if node has any predecessors."""
        return bool(self._predecessors[node])

    def descendants_bfs(self, node: T, /) -> Iterator[T]:
        """Return breadth first search of descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = {node}
        queue = collections.deque(self.successors(node))

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

        visited = {node}
        stack = collections.deque(self.successors(node))

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.successors(node2))
            yield node2

    def descendants(self, node: T, /) -> set[T]:
        """Return descendants of node."""
        return set(self.descendants_bfs(node))

    def descendants_subgraph(self, node: T, /) -> Self:
        """Return a subgraph of the descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        subgraph = type(self)()
        queue = collections.deque([node])

        while queue:
            node2 = queue.popleft()
            if node2 in subgraph:
                continue
            subgraph.add_node(node2)
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

        visited = {node}
        queue = collections.deque(self.predecessors(node))

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

        visited = {node}
        stack = collections.deque(self.predecessors(node))

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.predecessors(node2))
            yield node2

    def ancestors(self, node: T, /) -> set[T]:
        """Return ancestors of node."""
        return set(self.ancestors_bfs(node))

    def ancestors_subgraph(self, node: T, /) -> Self:
        """Return a subgraph of the ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        subgraph = type(self)()
        queue = collections.deque([node])

        while queue:
            node2 = queue.popleft()
            if node2 in subgraph:
                continue
            subgraph.add_node(node2)
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

        return target in self.descendants_dfs(source)

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

    def roots(self) -> Iterable[T]:
        """Return all roots of the graph."""
        for node in self:
            if not self.has_predecessors(node):
                yield node

    def leaves(self) -> Iterable[T]:
        """Return all leaves of the graph."""
        for node in self:
            if not self.has_successors(node):
                yield node
