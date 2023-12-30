"""Attributes and associated classes/exceptions."""

import dataclasses

from graft.domain.tasks.description import Description
from graft.domain.tasks.name import Name


@dataclasses.dataclass
class Attributes:
    """Attributes of a task."""

    name: Name | None = None
    description: Description | None = None

    def __eq__(self, other: object) -> bool:
        """Check if two attributes are equal."""
        if not isinstance(other, Attributes):
            return False

        return self.name == other.name and self.description == other.description


class AttributesView:
    """Attributes view."""

    def __init__(self, attributes: Attributes) -> None:
        """Initialise AttributesView."""
        self._attributes = attributes

    def __eq__(self, other: object) -> bool:
        """Check if two attributes views are equal."""
        if not isinstance(other, AttributesView):
            return False

        return self.name == other.name and self.description == other.description

    @property
    def name(self) -> Name | None:
        """Get name."""
        return self._attributes.name

    @property
    def description(self) -> Description | None:
        """Get description."""
        return self._attributes.description
