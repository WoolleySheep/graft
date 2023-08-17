"""Bi-directional multi-value dictionary and associated exceptions."""

from collections.abc import Hashable, Iterator
from typing import Any, Generic, TypeVar

T = TypeVar("T", bound=Hashable)


class KeyAlreadyExistsError(Exception):
    """Raised when key already exists."""

    def __init__(
        self,
        key: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize KeyAlreadyExistsError."""
        self.key = key
        super().__init__(f"key [{key}] already exists", *args, **kwargs)


class KeyDoesNotExistError(Exception):
    """Raised when key does not exist."""

    def __init__(
        self,
        key: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize KeyDoesNotExistError."""
        self.key = key
        super().__init__(f"key [{key}] does not exist", *args, **kwargs)


class ValueDoesNotExistError(Exception):
    """Raised when value does not exist."""

    def __init__(
        self,
        value: T,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize ValueDoesNotExistError."""
        self.value = value
        super().__init__(f"value [{value}] does not exist", *args, **kwargs)


class BiDirectionalMultiDict(Generic[T]):
    """Bi-directional multi-value dictionary.

    Each key can have multiple unique values associated with it, and vice-versa.
    """

    class InvertedMultiDict:
        """Inverted view of BiDirectionalMultiDict."""

        def __init__(
            self,
            backward: dict[T, set[T]],
        ) -> None:
            """Initialize InvertedMultiDict."""
            self._backward = backward

        def __contains__(self, value: T) -> bool:
            """Check if value exists in inverted multidict."""
            return value in self._backward

        def __getitem__(self, value: T) -> Iterator[T]:
            """Return iterator over keys of value."""
            if value not in self:
                raise ValueDoesNotExistError(value=value)

            yield from self._backward[value]

    def __init__(self) -> None:
        """Initialize bidict."""
        self._forward = dict[T, set[T]]()
        self._backward = dict[T, set[T]]()
        self.inverse = self.InvertedMultiDict(backward=self._backward)

    def __bool__(self) -> bool:
        """Check if bidict has any keys."""
        return bool(self._forward)

    def __contains__(self, key: T) -> bool:
        """Check if key exists in bidict."""
        return key in self._forward

    def __iter__(self) -> Iterator[T]:
        """Return iterator over keys."""
        return iter(self._forward)

    def __getitem__(self, key: T) -> Iterator[T]:
        """Return iterator over values of key."""
        if key not in self:
            raise KeyDoesNotExistError(key=key)

        yield from self._forward[key]

    def __delitem__(self, key: T) -> None:
        """Remove key and associated values."""
        if key not in self:
            raise KeyDoesNotExistError(key=key)

        for value in self._forward[key]:
            self._backward[value].remove(key)

        for value in self._backward[key]:
            self._forward[value].remove(key)

        del self._forward[key]
        del self._backward[key]

    def __str__(self) -> str:
        """Return string representation of bidict."""
        return str(self._forward)

    def __repr__(self) -> str:
        """Return string representation of bidict."""
        return repr(self._forward)

    def __len__(self) -> int:
        """Return number of keys in bidict."""
        return len(self._forward)

    def items(self) -> Iterator[tuple[T, Iterator[T]]]:
        """Return iterator over (key, value) pairs."""
        for key, values in self._forward.items():
            yield key, iter(values)

    def add(self, key: T, value: T | None = None) -> None:
        """Add value to values associated with key.

        If value is None, just create the key.
        """
        if key not in self:
            self._forward[key] = set[T]()
            self._backward[key] = set[T]()

        if value is not None:
            if value not in self:
                self._forward[value] = set[T]()
                self._backward[value] = set[T]()

            self._forward[key].add(value)
            self._backward[value].add(key)

    def remove(self, key: T, value: T) -> None:
        """Remove value from values associated with key."""
        if key not in self:
            raise KeyDoesNotExistError(key=key)

        if value not in self:
            raise ValueDoesNotExistError(value=value)

        self._forward[key].remove(value)
        self._backward[value].remove(key)
