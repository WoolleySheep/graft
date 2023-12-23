"""Task attributes and associated classes and exceptions."""

import enum
from collections.abc import Iterator, Set
from typing import Any, Self, TypedDict


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


class Name:
    """Task name."""

    def __init__(self, *, text: str) -> None:
        """Initialise Name."""
        self._text = text

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text


class Description:
    """Task description."""

    def __init__(self, *, text: str) -> None:
        """Initialise Description."""
        self._text = text

    def __str__(self) -> str:
        """Return description as a string."""
        return self._text


class Importance(enum.Enum):
    """Task importance.

    Note that when compared, "Medium" will evaluate as greater than "OPTIONAL".
    """

    OPTIONAL = "optional"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Attributes:
    """Task attributes."""

    def __init__(
        self,
        name: Name | None,
        description: Description | None,
        importance: Importance | None,
    ) -> None:
        """Initialise Attributes."""
        self.name = name
        self.description = description
        self.importance = importance


class AttributesView:
    """Attributes view."""

    def __init__(self, attributes: Attributes) -> None:
        """Initialise AttributesView."""
        self._attributes = attributes

    @property
    def name(self) -> Name | None:
        """Get name."""
        return self._attributes.name

    @property
    def description(self) -> Description | None:
        """Get description."""
        return self._attributes.description

    @property
    def importance(self) -> Importance | None:
        """Get importance."""
        return self._attributes.importance


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
        super().__init__(f"uid [{uid}] is not registered", *args, **kwargs)


class UIDsView(Iterator[UID]):
    """View of a set of task UIDs."""

    def __init__(self, tasks: Iterator[UID], /) -> None:
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