"""Attributes and associated classes/exceptions."""

from __future__ import annotations

import enum
from typing import TYPE_CHECKING, Protocol

from graft.domain.tasks.description import Description
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress

if TYPE_CHECKING:
    from graft.domain.tasks.importance import Importance


class DefaultSentinel(enum.Enum):
    """Sentinel for default values where None can't be used.

    Should only ever be one value, DEFAULT.
    """

    DEFAULT = enum.auto()


class IAttributesView(Protocol):
    """Interface for a view of attributes."""

    @property
    def name(self) -> Name:
        """Get name."""
        ...

    @property
    def description(self) -> Description:
        """Get description."""
        ...

    @property
    def progress(self) -> Progress | None:
        """Get progress."""
        ...

    @property
    def importance(self) -> Importance | None:
        """Get importance."""
        ...


class Attributes:
    """Attributes of a task."""

    def __init__(
        self,
        name: Name | None = None,
        description: Description | None = None,
        progress: Progress | None = Progress.NOT_STARTED,
        importance: Importance | None = None,
    ) -> None:
        if not name:
            name = Name()

        if not description:
            description = Description()

        self._name = name
        self._description = description
        self._progress = progress
        self._importance = importance

    def __str__(self) -> str:
        """Return string representation of attributes."""
        return f"{{name={self.name}, description={self.description}, progress={self.progress.name if self.progress else None}, importance={self.importance.name if self.importance else None}}}"

    def __repr__(self) -> str:
        """Return string representation of attributes."""
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r}, progress={(self.progress.name if self.progress else None)!r}, importance={(self.importance.name if self.importance else None)!r})"

    @property
    def name(self) -> Name:
        """Name of the task."""
        return self._name

    @property
    def description(self) -> Description:
        """Description of the task."""
        return self._description

    @property
    def progress(self) -> Progress | None:
        """Progress of the task."""
        return self._progress

    @property
    def importance(self) -> Importance | None:
        """Importance of the task."""
        return self._importance

    def copy(
        self,
        name: Name | None = None,
        description: Description | None = None,
        progress: Progress | None | DefaultSentinel = DefaultSentinel.DEFAULT,
        importance: Importance | None | DefaultSentinel = DefaultSentinel.DEFAULT,
    ) -> Attributes:
        """Copy the attributes with optional overrides.

        Need to use default sentinel values for progress and importance as None
        is a valid value.
        """
        return Attributes(
            name=name if name is not None else self.name,
            description=description if description is not None else self.description,
            progress=progress
            if progress is not DefaultSentinel.DEFAULT
            else self.progress,
            importance=importance
            if importance is not DefaultSentinel.DEFAULT
            else self.importance,
        )


class AttributesView:
    """Attributes view."""

    def __init__(self, attributes: IAttributesView) -> None:
        """Initialise AttributesView."""
        self._attributes = attributes

    def __eq__(self, other: object) -> bool:
        """Check if two attributes views are equal."""
        return (
            isinstance(other, AttributesView)
            and self.name == other.name
            and self.description == other.description
            and self.progress is other.progress
            and self.importance is other.importance
        )

    def __str__(self) -> str:
        """Return string representation of attributes."""
        return str(self._attributes)

    def __repr__(self) -> str:
        """Return string representation of attributes."""
        return f"{self.__class__.__name__}(name={self.name!r}, description={self.description!r}, progress={(self.progress.name if self.progress else None)!r}, importance={(self.importance.name if self.importance else None)!r})"

    @property
    def name(self) -> Name:
        """Get name."""
        return self._attributes.name

    @property
    def description(self) -> Description:
        """Get description."""
        return self._attributes.description

    @property
    def progress(self) -> Progress | None:
        """Get progress."""
        return self._attributes.progress

    @property
    def importance(self) -> Importance | None:
        """Get importance."""
        return self._attributes.importance
