"""Task Attributes and associated classes/exceptions."""

from graft.domain.events.description import Description
from graft.domain.events.name import Name


class Attributes:
    """Event attributes."""

    def __init__(
        self,
        name: Name | None = None,
        description: Description | None = None,
    ) -> None:
        """Initialise Attributes."""
        self.name = name
        self.description = description


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
