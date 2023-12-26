"""UID and associated classes/exceptions."""

from collections.abc import Collection, Iterator
from typing import Any


class InvalidUIDNumberError(Exception):
    """Invalid ID number error."""

    def __init__(
        self,
        number: int,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InvalidIDNumberError."""
        self.number = number
        super().__init__(f"Invalid ID number [{number}]", *args, **kwargs)


class UID:
    """Unique task identifier."""

    def __init__(self, /, number: int) -> None:
        """Initialise UID."""
        if number < 0:
            raise InvalidUIDNumberError(number=number)

        self._number = number

    def __hash__(self) -> int:
        """Return hash of the UID number."""
        return hash(self._number)

    def __int__(self) -> int:
        """Return UID number."""
        return self._number

    def __str__(self) -> str:
        """Return UID number as a string."""
        return str(self._number)


class UIDsView(Collection[UID]):
    """View of a set of task UIDs."""

    def __init__(self, tasks: Collection[UID], /) -> None:
        """Initialise UIDsView."""
        self._tasks = tasks

    def __bool__(self) -> bool:
        """Check view has any tasks."""
        return bool(self._tasks)

    def __len__(self) -> int:
        """Return number of tasks in view."""
        return len(self._tasks)

    def __contains__(self, item: object) -> bool:
        """Check if item is in TaskUIDsView."""
        return item in self._tasks

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over tasks in view."""
        return iter(self._tasks)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"uids_view({{{', '.join(str(task) for task in self._tasks)}}})"
