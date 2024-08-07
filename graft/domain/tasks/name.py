"""Name and associated classes/exceptions."""


class Name:
    """Task name."""

    def __init__(self, text: str = "", /) -> None:
        """Initialise Name."""
        self._text = text

    def __bool__(self) -> bool:
        """Return True if name is not empty."""
        return bool(self._text)

    def __eq__(self, other: object) -> bool:
        """Return True if equal."""
        return isinstance(other, Name) and self._text == str(other)

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text

    def __repr__(self) -> str:
        """Return name as a string for developers."""
        return f"Name({self._text})"
