from collections.abc import Hashable, Iterator
from typing import Protocol


class IEdgesView[T: Hashable](Protocol):
    """Abstract view of a collection of unique edges."""

    def __bool__(self) -> bool:
        """Check if there are any edges in the collection."""
        ...

    def __len__(self) -> int:
        """Return number of edges in the collection."""
        ...

    def __contains__(self, edge: tuple[T, T]) -> bool:
        """Check if edge is in the collection."""
        ...

    def __iter__(self) -> Iterator[tuple[T, T]]:
        """Return iterator over the edges."""
        ...
