"""Description and associated classes/exceptions."""


class Description:
    """Task description."""

    def __init__(self, text: str = "", /) -> None:
        """Initialise Description."""
        self._text = text

    def __bool__(self) -> bool:
        """Return True if description is not zero characters long."""
        return bool(self._text)

    def __len__(self) -> int:
        """Return number of characters in description."""
        return len(self._text)

    def __eq__(self, other: object) -> bool:
        """Return True if equal."""
        return isinstance(other, Description) and str(self) == str(other)

    def __str__(self) -> str:
        """Return description as a string."""
        return self._text

    def __repr__(self) -> str:
        """Return description as a string for developers."""
        return f"{self.__class__.__name__}({self._text})"
