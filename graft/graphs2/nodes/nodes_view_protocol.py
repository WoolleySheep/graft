from collections.abc import Hashable, Iterator
from typing import Protocol


class INodesView[T: Hashable](Protocol):
    """Abstract view of a collection of unique nodes."""

    def __bool__(self) -> bool:
        """Check if there are any nodes in the collection."""
        ...

    def __len__(self) -> int:
        """Return number of nodes in the collection."""
        ...

    def __contains__(self, node: T) -> bool:
        """Check if node is in the collection."""
        ...

    def __iter__(self) -> Iterator[T]:
        """Return iterator over the nodes."""
        ...
