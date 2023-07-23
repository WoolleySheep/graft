"""DiGraph and associated Exceptions."""

from collections.abc import Hashable
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
