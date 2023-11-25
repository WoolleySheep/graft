"""Bi-directional dictionary with set-like values and associated exceptions."""

from collections.abc import (
    Hashable,
    ItemsView,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Set,
    ValuesView,
)
from typing import Any, FrozenSet


class KeyAlreadyExistsError[T: Hashable](Exception):
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


class KeyDoesNotExistError[T: Hashable](Exception):
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


class ValueDoesNotExistError[T: Hashable](Exception):
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


class SetView[T: Hashable](Set[T]):
    """View of a set."""

    def __init__(self, set_: Set[T], /) -> None:
        """Initialize SetView."""
        self._set: Set[T] = set_

    def __bool__(self) -> bool:
        """Check if SetView has any values."""
        return bool(self._set)

    def __contains__(self, item: object) -> bool:
        """Check if item is in the set."""
        return item in self._set

    def __iter__(self) -> Iterator[T]:
        """Return iterator over values in the set."""
        return iter(self._set)

    def __len__(self) -> int:
        """Return number of values in the set."""
        return len(self._set)

    def __str__(self) -> str:
        """Return string representation of the set."""
        return f"set_view({{{', '.join(str(value) for value in self._set)}}})"


class SetViewMapping[T: Hashable, S: Hashable](Mapping[T, SetView[S]]):
    """Mapping with set-like view values."""

    def __init__(self, mapping: Mapping[T, Set[S]], /) -> None:
        """Initialise SetViewMapping."""
        self._mapping: Mapping[T, Set[S]] = mapping

    def __iter__(self) -> Iterator[T]:
        """Return iterator over keys in the mapping."""
        return iter(self._mapping)

    def __len__(self) -> int:
        """Return number of keys in the mapping."""
        return len(self._mapping)

    def __getitem__(self, key: T) -> SetView[S]:
        """Return SetView of values associated with key."""
        try:
            values: Set[S] = self._mapping[key]
        except KeyError as e:
            raise KeyDoesNotExistError(key) from e

        return SetView[S](values)

    def __str__(self) -> str:
        """Return string representation of the SetValuesMappingView."""
        keys_with_values: list[str] = []
        for key, values in self._mapping.items():
            keys_with_values.append(
                f"{key}: set_view({{{', '.join(str(value) for value in values)}}})",
            )
        return f"set_view_mapping({', '.join(keys_with_values)})"


class BiDirectionalSetValueDict[T: Hashable](MutableMapping[T, SetView[T]]):
    """Bi-directional dictionary with set-like values.

    Each key can have multiple unique values associated with it, and vice-versa.
    """

    def __init__(self) -> None:
        """Initialize bidict."""
        self._forward = dict[T, set[T]]()
        self._backward = dict[T, set[T]]()
        self.inverse = SetViewMapping[T, T](self._backward)

    def __bool__(self) -> bool:
        """Check if bidict has any keys."""
        return bool(self._forward)

    def __contains__(self, item: object) -> bool:
        """Check if item exists in SetValueMapping."""
        return item in self._forward

    def __iter__(self) -> Iterator[T]:
        """Return iterator over keys."""
        return iter(self._forward)

    def __getitem__(self, key: T) -> SetView[T]:
        """Return SetView over values of key."""
        try:
            values = self._forward[key]
        except KeyError as e:
            raise KeyDoesNotExistError(key=key) from e

        return SetView[T](values)

    def __delitem__(self, key: T) -> None:
        """Remove key and associated values from bidict."""
        if key not in self:
            raise KeyDoesNotExistError(key=key)

        for value in self._forward[key]:
            self._backward[value].remove(key)

        for value in self._backward[key]:
            self._forward[value].remove(key)

        del self._forward[key]
        del self._backward[key]

    def __setitem__(self, key: T, values: SetView[T]) -> None:
        """Set key and associated values in bidict."""
        del self[key]

        for value in values:
            self.add(key=key, value=value)

    def __str__(self) -> str:
        """Return string representation of bidict."""
        return f"bi_directional_set_value_dict({self._forward})"

    def __len__(self) -> int:
        """Return number of keys in bidict."""
        return len(self._forward)

    def keys(self) -> KeysView[T]:
        """Return KeysView of bidict."""
        return self._forward.keys()

    def values(self) -> ValuesView[SetView[T]]:
        """Return ValuesView of bidict."""
        return SetViewMapping[T, T](self._forward).values()

    def items(self) -> ItemsView[T, SetView[T]]:
        """Return ItemsView of bidict."""
        return SetViewMapping[T, T](self._forward).items()

    def add(self, key: T, value: T | None = None) -> None:
        """Add value to values associated with key.

        If key does not exist, create it.
        If value does not exist, create it.
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
        """Remove value from values associated with key.

        If the value is not associated with they key, nothing will happen.
        """
        if key not in self:
            raise KeyDoesNotExistError(key=key)

        if value not in self:
            raise ValueDoesNotExistError(value=value)

        self._forward[key].remove(value)
        self._backward[value].remove(key)
