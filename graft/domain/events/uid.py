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
        """Initialize InvalidUIDNumberError."""
        self.number = number
        super().__init__(f"Invalid UID number [{number}]", *args, **kwargs)


class UID:
    """Unique event identifier."""

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


class UIDAlreadyExistsError(Exception):
    """Raised when UID already exists."""

    def __init__(
        self,
        uid: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize UIDAlreadyExistsError."""
        self.uid = uid
        super().__init__(f"uid [{uid}] already exists", *args, **kwargs)


class UIDDoesNotExistError(Exception):
    """Raised when UID does not exist."""

    def __init__(
        self,
        uid: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize UIDDoesNotExistError."""
        self.uid = uid
        super().__init__(f"uid [{uid}] does not exist", *args, **kwargs)


class UIDsView(Collection[UID]):
    """View of a set of event UIDs."""

    def __init__(self, events: Collection[UID], /) -> None:
        """Initialise UIDsView."""
        self._events = events

    def __bool__(self) -> bool:
        """Check view has any events."""
        return bool(self._events)

    def __len__(self) -> int:
        """Return number of events in view."""
        return len(self._events)

    def __contains__(self, item: object) -> bool:
        """Check if item is in view."""
        return item in self._events

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over events in view."""
        return iter(self._events)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"uids_view({{{', '.join(str(task) for task in self._events)}}})"
