"""Name and associated classes/exceptions."""


class Name:
    """Task name."""

    def __init__(self, /, text: str) -> None:
        """Initialise Name."""
        self._text = text

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text
