"""UID and associated classes/exceptions."""

from __future__ import annotations

from collections.abc import Generator, Iterable, Iterator, Set
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from graft import graphs


class InvalidUIDNumberError(Exception):
    """Invalid ID number error."""

    def __init__(
        self,
        number: int,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InvalidIDNumberError."""
        self.number = number
        super().__init__(f"Invalid ID number [{number}]", *args, **kwargs)


class UID:
    """Unique task identifier."""

    def __init__(self, number: int, /) -> None:
        """Initialise UID."""
        if number < 0:
            raise InvalidUIDNumberError(number=number)

        self._number = number

    def __eq__(self, other: object) -> bool:
        """Check if UID is equal to other."""
        return isinstance(other, UID) and int(self) == int(other)

    def __lt__(self, other: UID) -> bool:
        """Check if UID is less than other."""
        return int(self) < int(other)

    def __hash__(self) -> int:
        """Return hash of the UID number."""
        return hash(self._number)

    def __int__(self) -> int:
        """Return UID number."""
        return self._number

    def __str__(self) -> str:
        """Return string representation of UID."""
        return str(self._number)

    def __repr__(self) -> str:
        """Return string representation of UID."""
        return f"uid({self._number!r})"


class TasksView(Set[UID]):
    """View of a set of tasks."""

    def __init__(self, tasks: Set[UID], /) -> None:
        self._tasks = tasks

    def __bool__(self) -> bool:
        """Check view has any tasks."""
        return bool(self._tasks)

    def __len__(self) -> int:
        """Return number of tasks in view."""
        return len(self._tasks)

    def __contains__(self, item: object) -> bool:
        """Check if item is in TaskUIDsView."""
        return item in self._tasks

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over tasks in view."""
        return iter(self._tasks)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return (
            isinstance(other, TasksView)
            and len(self) == len(other)
            and all(task in other for task in self)
        )

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"{{{', '.join(str(task) for task in self._tasks)}}}"

    def __repr__(self) -> str:
        """Return string representation of view."""
        return f"tasks_view({', '.join(repr(task) for task in self._tasks)})"

    def __sub__(self, other: Set[Any]) -> TasksView:
        """Return difference of two views."""
        return TasksView(self._tasks - other)

    def __and__(self, other: Set[Any]) -> TasksView:
        """Return intersection of two views."""
        return TasksView(self._tasks & other)

    def __or__(self, other: Set[UID]) -> TasksView:
        """Return union of two views."""
        return TasksView(self._tasks | other)

    def __xor__(self, other: Set[UID]) -> TasksView:
        """Return symmetric difference of two views."""
        return TasksView(self._tasks ^ other)


class SubgraphTasksView(Set[UID]):
    """View of a set of task UIDs in a subgraph."""

    def __init__(self, subgraph_nodes: graphs.SubgraphNodesView[UID]) -> None:
        self._subgraph_nodes = subgraph_nodes

    def __bool__(self) -> bool:
        """Check if subgraph has any tasks."""
        return bool(self._subgraph_nodes)

    def __len__(self) -> int:
        """Return number of tasks in subgraph."""
        return len(self._subgraph_nodes)

    def __contains__(self, item: object) -> bool:
        """Check if item is a task in the subgraph."""
        return item in self._subgraph_nodes

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over tasks in view."""
        return iter(self._subgraph_nodes)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return isinstance(other, SubgraphTasksView) and set(self) == set(other)

    def contains(self, tasks: Iterable[UID]) -> Generator[bool, None, None]:
        """Check if tasks are in the subgraph.

        Theoretically faster than checking if the subgraph contains multiple tasks
        one at a time, as can cache the parts of the subgraph already searched.
        """
        return self._subgraph_nodes.contains(tasks)

    def __sub__(self, other: Set[Any]) -> SubgraphTasksView:
        """Return difference of two views."""
        raise NotImplementedError

    def __and__(self, other: Set[Any]) -> SubgraphTasksView:
        """Return intersection of two views."""
        raise NotImplementedError

    def __or__(self, other: Set[UID]) -> SubgraphTasksView:
        """Return union of two views."""
        raise NotImplementedError

    def __xor__(self, other: Set[UID]) -> SubgraphTasksView:
        """Return symmetric difference of two views."""
        raise NotImplementedError
