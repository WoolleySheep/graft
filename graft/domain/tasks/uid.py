"""UID and associated classes/exceptions."""

from __future__ import annotations

from collections.abc import Hashable, Set
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterator


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

    def __init__(self, number: int, /) -> None:
        """Initialise UID."""
        if number < 0:
            raise InvalidUIDNumberError(number=number)

        self._number = number

    def __eq__(self, other: object) -> bool:
        """Check if UID is equal to other."""
        if not isinstance(other, UID):
            return NotImplemented
        return int(self) == int(other)

    def __lt__(self, other: UID) -> bool:
        """Check if UID is less than other."""
        return int(self) < int(other)

    def __hash__(self) -> int:
        """Return hash of the UID number."""
        return hash(self._number)

    def __int__(self) -> int:
        """Return UID number."""
        return self._number

    def __str__(self) -> str:
        """Return string representation of UID."""
        return str(self._number)

    def __repr__(self) -> str:
        """Return string representation of UID."""
        return f"uid({self._number!r})"


class TasksView(Set[UID]):
    """View of a set of tasks."""

    def __init__(self, tasks: Set[UID], /) -> None:
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

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        if not isinstance(other, TasksView):
            return NotImplemented

        return set(self._tasks) == set(other)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"{{{', '.join(str(task) for task in self._tasks)}}}"

    def __repr__(self) -> str:
        """Return string representation of view."""
        return f"tasks_view({', '.join(repr(task) for task in self._tasks)})"

    def __sub__(self, other: Set[Any]) -> set[UID]:
        """Return difference of two views."""
        return set(self._tasks - other)

    def __and__(self, other: Set[Any]) -> set[UID]:
        """Return intersection of two views."""
        return set(self._tasks & other)

    def __or__[G: Hashable](self, other: Set[G]) -> set[UID | G]:
        """Return union of two views."""
        return set(self._tasks | other)

    def __xor__[G: Hashable](self, other: Set[G]) -> set[UID | G]:
        """Return symmetric difference of two views."""
        return set(self._tasks ^ other)

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return self._tasks <= other

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self._tasks < other

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return self._tasks >= other

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self._tasks > other
