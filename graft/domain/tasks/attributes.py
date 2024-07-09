"""Attributes and associated classes/exceptions."""

import dataclasses

from graft.domain.tasks.description import Description
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress


@dataclasses.dataclass
class Attributes:
    """Attributes of a task."""

    name: Name = dataclasses.field(default_factory=Name)
    description: Description = dataclasses.field(default_factory=Description)
    progress: Progress | None = Progress.NOT_STARTED
    importance: Importance | None = None

    def __eq__(self, other: object) -> bool:
        """Check if two attributes are equal."""
        return (
            isinstance(other, Attributes)
            and self.name == other.name
            and self.description == other.description
            and self.progress is other.progress
            and self.importance is other.importance
        )


class AttributesView:
    """Attributes view."""

    def __init__(self, attributes: Attributes) -> None:
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
