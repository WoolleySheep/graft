"""Event and associated classes and exceptions."""

import datetime as dt
from typing import Any
import copy


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
    """Unique event identifier."""

    def __init__(self, *, number: int) -> None:
        """Initialise UID."""
        if number < 0:
            raise InvalidUIDNumberError(number=number)

        self._number = number

    def __int__(self) -> int:
        return self._number


class Name:
    """Event name."""

    def __init__(self, *, text: str) -> None:
        """Initialise Name."""
        self._text = text

    def __str__(self) -> str:
        return self._text


class Description:
    """Event description."""

    def __init__(self, *, text: str) -> None:
        """Initialise Description."""
        self._text = text

    def __str__(self) -> str:
        return self._text


class Event:
    """Event."""

    def __init__(
        self,
        uid: UID,
        name: Name | None = None,
        description: Description | None = None,
        datetime: dt.datetime | None = None,
    ) -> None:
        """Initialise Event."""
        self.uid = uid
        self.name = name
        self.description = description
        self.datetime = datetime
