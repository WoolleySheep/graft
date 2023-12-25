from graft.domain.task.description import Description
from graft.domain.task.name import Name


class Attributes:
    """Task attributes."""

    def __init__(
        self,
        name: Name | None,
        description: Description | None,
    ) -> None:
        """Initialise Attributes."""
        self.name = name
        self.description = description


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
