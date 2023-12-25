from typing import Any


class InvalidUIDNumberError(Exception):
    """Invalid ID number error."""

    def __init__(
        self,
        number: int,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InvalidUIDNumberError."""
        self.number = number
        super().__init__(f"Invalid UID number [{number}]", *args, **kwargs)


class UID:
    """Unique event identifier."""

    def __init__(self, /, number: int) -> None:
        """Initialise UID."""
        if number < 0:
            raise InvalidUIDNumberError(number=number)

        self._number = number

    def __hash__(self) -> int:
        """Return hash of the UID number."""
        return hash(self._number)

    def __int__(self) -> int:
        """Return UID number."""
        return self._number


class UIDAlreadyExistsError(Exception):
    """Raised when UID already exists."""

    def __init__(
        self,
        uid: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize UIDAlreadyExistsError."""
        self.uid = uid
        super().__init__(f"uid [{uid}] already exists", *args, **kwargs)


class UIDDoesNotExistError(Exception):
    """Raised when UID does not exist."""

    def __init__(
        self,
        uid: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize UIDDoesNotExistError."""
        self.uid = uid
        super().__init__(f"uid [{uid}] does not exist", *args, **kwargs)
