"""Description and associated classes/exceptions."""


class Description:
    """Event description."""

    def __init__(self, /, text: str) -> None:
        """Initialise Description."""
        self._text = text

    def __str__(self) -> str:
        """Return description as a string."""
        return self._text
