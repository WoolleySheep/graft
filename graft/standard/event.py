"""Event and associated classes and exceptions."""

import datetime
from typing import Any


class InvalidUIDValueError(Exception):
    """Invalid ID value error."""

    def __init__(
        self,
        value: int,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InvalidIDValueError."""
        self.value = value
        super().__init__(f"Invalid ID value [{value}]", *args, **kwargs)


class UID:
    """Unique event identifier."""

    def __init__(self, value: int) -> None:
        """Initialise UID."""
        if value < 0:
            raise InvalidUIDValueError(value=value)

        self.value = value


class Name:
    """Event name."""

    def __init__(self, text: str) -> None:
        """Initialise Name."""
        self.text = text


class Description:
    """Event description."""

    def __init__(self, text: str) -> None:
        """Initialise Description."""
        self.text = text


class Event:
    """Event."""

    def __init__(
        self,
        uid: UID | None = None,
        name: Name | None = None,
        description: Description | None = None,
        datetime: datetime.datetime | None = None,
    ) -> None:
        """Initialise Event."""
        self.uid = uid
        self.name = name
        self.description = description
        self.datetime = datetime
