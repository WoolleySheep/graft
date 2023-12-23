"""Event and associated classes and exceptions."""

import datetime as dt
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


class Name:
    """Event name."""

    def __init__(self, *, text: str) -> None:
        """Initialise Name."""
        self._text = text

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text


class Description:
    """Event description."""

    def __init__(self, *, text: str) -> None:
        """Initialise Description."""
        self._text = text

    def __str__(self) -> str:
        """Return description as a string."""
        return self._text


class Attributes:
    """Event attributes."""

    def __init__(
        self,
        name: Name | None = None,
        description: Description | None = None,
        datetime: dt.datetime | None = None,
    ) -> None:
        """Initialise Attributes."""
        self.name = name
        self.description = description
        self.datetime = datetime  # When event occurs


class AttributesView:
    """View of event attributes."""

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
    def datetime(self) -> dt.datetime | None:
        """Get datetime when event occurs."""
        return self._attributes.datetime


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
