from __future__ import annotations

import itertools
from collections.abc import (
    Container,
    Hashable,
    Iterable,
    Sequence,
    Set,
)
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
        Iterator,
    )


class LazyContainer[T: Hashable](Container[T]):
    """Container that lazily tests membership, keep a record for subsequent tests."""

    def __init__(self, values: Iterable[T]) -> None:
        self._uniterated_values = iter(values)
        self._iterated_values = set[T]()

    def __contains__(self, value: object) -> bool:
        """Check if value is in the container."""
        if value in self._iterated_values:
            return True

        for item in self._uniterated_values:
            self._iterated_values.add(item)

            if item == value:
                return True

        return False


class CheckableIterable[T](Iterable[T]):
    """Decorator for an iterable that lets you check if it's empty."""

    def __init__(self, iterable: Iterable[T]) -> None:
        self._iterable = iter(iterable)
        self._first_value: T | None = None

    def __iter__(self) -> Iterator[T]:
        if self._first_value is not None:
            value = self._first_value
            self._first_value = None
            yield value
        yield from self._iterable

    def __bool__(self) -> bool:
        """Check if the iterable contains any values (without consuming it)."""
        if self._first_value is not None:
            return True
        try:
            self._first_value = next(self._iterable)
        except StopIteration:
            return False
        return True


class LazyFrozenSet[T: Hashable](Set[T]):
    """Frozen set that evaluates lazily."""

    def __init__(self, values: Iterable[T]) -> None:
        self._uniterated_values = iter(values)
        self._iterated_values = set[T]()
        self._fully_iterated = False

    def _ensure_fully_iterated(self) -> None:
        if not self._fully_iterated:
            self._iterated_values.update(self._uniterated_values)
            self._fully_iterated = True

    def __bool__(self) -> bool:
        """Truth value testing."""
        if self._iterated_values:
            return True

        try:
            value = next(self._uniterated_values)
        except StopIteration:
            self._fully_iterated = True
            return False
        self._iterated_values.add(value)
        return True

    def __contains__(self, value: object) -> bool:
        if value in self._iterated_values:
            return True
        for item in self._uniterated_values:
            self._iterated_values.add(item)
            if item == value:
                return True
        self._fully_iterated = True
        return False

    def __iter__(self) -> Iterator[T]:
        yield from self._iterated_values
        for item in self._uniterated_values:
            if item in self._iterated_values:
                continue
            self._iterated_values.add(item)
            yield item
        self._fully_iterated = True

    def __len__(self) -> int:
        self._ensure_fully_iterated()
        return len(self._iterated_values)

    def __hash__(self) -> int:
        self._ensure_fully_iterated()
        return hash(frozenset(self._iterated_values))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LazyFrozenSet):
            return NotImplemented

        self._ensure_fully_iterated()
        return self._iterated_values == set(other)

    def __and__[G: Hashable](self, other: Set[G]) -> LazyFrozenSet[T]:
        """Intersection operation (self & other)."""
        return LazyFrozenSet(item for item in self if item in other)

    def __or__[G: Hashable](self, other: Set[G]) -> LazyFrozenSet[T | G]:
        """Union operation (self | other)."""
        return LazyFrozenSet(unique(itertools.chain(self, other)))

    def __sub__[G: Hashable](self, other: Set[G]) -> LazyFrozenSet[T]:
        """Difference operation (self - other)."""
        return LazyFrozenSet(item for item in self if item not in other)

    def __xor__[G: Hashable](self, other: Set[G]) -> LazyFrozenSet[T | G]:
        """Symmetric difference operation (self ^ other)."""
        return LazyFrozenSet(
            unique(
                itertools.chain(
                    (item for item in self if item not in other),
                    (item for item in other if item not in self),
                )
            )
        )

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return all(item in other for item in self)

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self <= other and len(self) < len(other)

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return all(item in self for item in other)

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self >= other and len(self) > len(other)


class LazyTuple[T](Sequence[T]):
    """Tuple that evaluates lazily."""

    def __init__(self, values: Iterable[T]) -> None:
        self._uniterated_values = iter(values)
        self._iterated_values: list[T] = []
        self._fully_iterated = False

    def _ensure_index(self, index: int) -> None:
        """Ensure we have iterated up to the given (positive) index."""
        while len(self._iterated_values) <= index and not self._fully_iterated:
            try:
                value = next(self._uniterated_values)
            except StopIteration:
                self._fully_iterated = True
                break
            self._iterated_values.append(value)

    def _ensure_fully_iterated(self) -> None:
        if not self._fully_iterated:
            self._iterated_values.extend(self._uniterated_values)
            self._fully_iterated = True

    @overload
    def __getitem__(self, index: int) -> T: ...

    @overload
    def __getitem__(self, index: slice) -> LazyTuple[T]: ...

    def __getitem__(self, index: int | slice) -> T | LazyTuple[T]:
        if isinstance(index, slice):
            self._ensure_fully_iterated()
            return LazyTuple(self._iterated_values[index])
        if index < 0:
            self._ensure_fully_iterated()
            return self._iterated_values[index]
        self._ensure_index(index)
        return self._iterated_values[index]

    def __len__(self) -> int:
        self._ensure_fully_iterated()
        return len(self._iterated_values)

    def __iter__(self) -> Generator[T, None, None]:
        yield from self._iterated_values
        for item in self._uniterated_values:
            self._iterated_values.append(item)
            yield item
        self._fully_iterated = True

    def __contains__(self, value: object) -> bool:
        if value in self._iterated_values:
            return True
        for item in self._uniterated_values:
            self._iterated_values.append(item)
            if item == value:
                return True
        self._fully_iterated = True
        return False

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (list, LazyTuple)):
            return NotImplemented
        self._ensure_fully_iterated()
        return self._iterated_values == list(other)

    def __hash__(self) -> int:
        self._ensure_fully_iterated()
        return hash(tuple(self._iterated_values))

    def __bool__(self) -> bool:
        if self._iterated_values:
            return True
        try:
            value = next(self._uniterated_values)
        except StopIteration:
            self._fully_iterated = True
            return False
        self._iterated_values.append(value)
        return True


def unique[T](iterable: Iterable[T]) -> Generator[T, None, None]:
    """Yield unique items from an iterable."""
    seen = set[T]()
    for item in iterable:
        if item in seen:
            continue
        seen.add(item)
        yield item


def lazy_intersection[T: Hashable](
    a: Iterable[T], b: Iterable[T]
) -> Generator[T, None, None]:
    """Lazily yield the intersection of two iterables."""
    a_iter = iter(a)
    b_iter = iter(b)
    a2 = set[T]()
    b2 = set[T]()

    for a_value in a_iter:
        if a_value in a2:
            continue
        a2.add(a_value)
        if a_value in b2:
            yield a_value
            continue
        for b_value in b_iter:
            b2.add(b_value)
            if b_value == a_value:
                yield a_value
                break


def group_by_hashable[T, G: Hashable](
    iterable: Iterable[T], key: Callable[[T], G]
) -> dict[G, list[T]]:
    """Group items by a key function that returns a hashable value.

    Allows grouping in O(n) time.
    """
    key_value_to_group_map = dict[G, list[T]]()
    for item in iterable:
        key_value = key(item)
        if key_value not in key_value_to_group_map:
            key_value_to_group_map[key_value] = []
        key_value_to_group_map[key_value].append(item)
    return key_value_to_group_map
