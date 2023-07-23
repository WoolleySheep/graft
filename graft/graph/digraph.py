"""DiGraph and associated Exceptions."""

from __future__ import annotations

import collections
import contextlib
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

    def add_node(self, node: T) -> None:
        """Add node to DiGraph."""
        if node in self:
            raise NodeAlreadyExistsError(node=node)

        self._successors[node] = set()
        self._predecessors[node] = set()

    def remove_node(self, node: T) -> None:
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

    def successors(self, node: T) -> Iterator[T]:
        """Return successors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._successors[node]

    def has_successor(self, node: T, successor: T) -> bool:
        """Check if node has successor."""
        return self._has_edge(source=node, target=successor)

    def has_successors(self, node: T) -> bool:
        """Check if node has successors."""
        return bool(self._successors[node])

    def predecessors(self, node: T) -> Iterator[T]:
        """Return predecessors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        yield from self._predecessors[node]

    def has_predecessor(self, node: T, predecessor: T) -> bool:
        """Check if node has predecessor."""
        return self._has_edge(source=predecessor, target=node)

    def has_predecessors(self, node: T) -> bool:
        """Check if node has predecessors."""
        return bool(self._predecessors[node])

    def descendants_bfs(self, node: T) -> Iterator[T]:
        """Return breadth first search of descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = {node}
        queue = collections.deque(self.successors(node=node))

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.successors(node2))
            yield node2

    def descendants_dfs(self, node: T) -> Iterator[T]:
        """Return depth first search of the descendants of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = {node}
        stack = collections.deque(self.successors(node=node))

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.successors(node2))
            yield node2

    def descendants(self, node: T) -> set[T]:
        """Return descendants of node."""
        return set(self.descendants_bfs(node=node))

    def ancestors_bfs(self, node: T) -> Iterator[T]:
        """Return breadth first search of ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = {node}
        queue = collections.deque(self.predecessors(node=node))

        while queue:
            node2 = queue.popleft()
            if node2 in visited:
                continue
            visited.add(node2)
            queue.extend(self.predecessors(node2))
            yield node2

    def ancestors_dfs(self, node: T) -> Iterator[T]:
        """Return depth first search of ancestors of node."""
        if node not in self:
            raise NodeDoesNotExistError(node=node)

        visited = {node}
        stack = collections.deque(self.predecessors(node=node))

        while stack:
            node2 = stack.pop()
            if node2 in visited:
                continue
            visited.add(node2)
            stack.extend(self.predecessors(node2))
            yield node2

    def ancestors(self, node: T) -> set[T]:
        """Return ancestors of node."""
        return set(self.ancestors_bfs(node=node))

    def has_path(self, source: T, target: T) -> bool:
        """Check if there is a path from source to target."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        return target in self.descendants_dfs(node=source)

    def connecting_subgraph(self, source: T, target: T) -> Self:
        """Return connecting subgraph from source to target."""
        for node in [source, target]:
            if node not in self:
                raise NodeDoesNotExistError(node=node)

        # Iterate forward through the graph to generate a map of nodes and all
        # their predecessors who are also in the map
        queue = collections.deque(self.successors(node=source))
        predecessors_in_subgraph = collections.defaultdict(
            set,
            ((node, {source}) for node in queue),
        )

        while queue:
            node = queue.popleft()
            for successor in self.successors(node=node):
                if successor not in predecessors_in_subgraph:
                    queue.append(successor)
                predecessors_in_subgraph[successor].add(node)

        if target not in predecessors_in_subgraph:
            raise NoConnectingSubgraphError(source=source, target=target)

        # Iterate backward through the map from the target to get the subgraph
        # from source to target
        subgraph = type(self)()
        subgraph.add_node(node=target)
        visited = set()
        stack = collections.deque([target])
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            for predecessor in predecessors_in_subgraph[node]:
                with contextlib.suppress(NodeAlreadyExistsError):
                    subgraph.add_node(node=predecessor)
                subgraph.add_edge(source=predecessor, target=node)
            stack.extend(predecessors_in_subgraph[node])

        return subgraph
