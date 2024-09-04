"""Name and associated classes/exceptions."""


class Name:
    """Task name."""

    def __init__(self, text: str = "", /) -> None:
        """Initialise Name."""
        self._text = text

    def __bool__(self) -> bool:
        """Return True if name is not zero characters long."""
        return bool(self._text)

    def __len__(self) -> int:
        """Return number of characters in name."""
        return len(self._text)

    def __eq__(self, other: object) -> bool:
        """Return True if equal."""
        return isinstance(other, Name) and str(self) == str(other)

    def __str__(self) -> str:
        """Return name as a string."""
        return self._text

    def __repr__(self) -> str:
        """Return name as a string for developers."""
        return f"{self.__class__.__name__}({self._text!r})"
