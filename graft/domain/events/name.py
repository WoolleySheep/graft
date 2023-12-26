"""Name and associated classes/exceptions."""


class Name:
    """Event name."""

    def __init__(self, /, text: str) -> None:
        """Initialise Name."""
        self._text = text

    def __eq__(self, other: object) -> bool:
        """Return True if equal."""
        return isinstance(other, Name) and self._text == str(other)

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text
