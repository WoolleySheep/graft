"""Attributes and associated classes/exceptions."""

import dataclasses

from graft.domain.events.description import Description
from graft.domain.events.name import Name


@dataclasses.dataclass
class Attributes:
    """Attributes of an event."""

    name: Name | None = None
    description: Description | None = None


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
