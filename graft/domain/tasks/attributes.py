"""Attributes and associated classes/exceptions."""

import dataclasses

from graft.domain.tasks.description import Description
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress


@dataclasses.dataclass
class Attributes:
    """Attributes of a task.

    Progress should only be None when the task is non-concrete (aka: its
    progress is dependent upon the progress of its subtasks).
    """

    name: Name | None = None
    description: Description | None = None
    progress: Progress | None = Progress.NOT_STARTED

    def __eq__(self, other: object) -> bool:
        """Check if two attributes are equal."""
        return (
            isinstance(other, Attributes)
            and self.name == other.name
            and self.description == other.description
            and self.progress is other.progress
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
        )

    @property
    def name(self) -> Name | None:
        """Get name."""
        return self._attributes.name

    @property
    def description(self) -> Description | None:
        """Get description."""
        return self._attributes.description

    @property
    def progress(self) -> Progress | None:
        """Get progress."""
        return self._attributes.progress
