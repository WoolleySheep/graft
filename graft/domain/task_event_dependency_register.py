from collections.abc import Collection, Generator, Iterator, Set

from graft.domain import event, task


class TaskUIDsView(Collection[task.UID]):
    """View of a collection of task UIDs."""

    def __init__(self, tasks: Collection[task.UID], /) -> None:
        """Initialise TaskUIDsView."""
        self._tasks: Collection[task.UID] = tasks

    def __bool__(self) -> bool:
        """Check view has any tasks."""
        return bool(self._tasks)

    def __len__(self) -> int:
        """Return number of tasks in view."""
        return len(self._tasks)

    def __contains__(self, item: object) -> bool:
        """Check if item is in TaskUIDsView."""
        return item in self._tasks

    def __iter__(self) -> Iterator[task.UID]:
        """Return iterator over tasks in view."""
        return iter(self._tasks)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"task_uids_view({{{', '.join(str(task) for task in self._tasks)}}})"


class EventUIDsView(Collection[event.UID]):
    """View of a collection of event UIDs."""

    def __init__(self, events: Collection[event.UID], /) -> None:
        """Initialise EventUIDsView."""
        self._events: Collection[event.UID] = events

    def __bool__(self) -> bool:
        """Check view has any events."""
        return bool(self._events)

    def __len__(self) -> int:
        """Return number of events in view."""
        return len(self._events)

    def __contains__(self, item: object) -> bool:
        """Check if item is in EventUIDsView."""
        return item in self._events

    def __iter__(self) -> Iterator[event.UID]:
        """Return iterator over events in view."""
        return iter(self._events)

    def __str__(self) -> str:
        """Return string representation of view."""
        return f"event_uids_view({{{', '.join(str(event) for event in self._events)}}})"


class TaskEventDependencyRegister:
    """Dependencies between tasks and events.

    For now this only captures tasks and the events they're due by. Eventually,
    tasks will also be able to use events as start-after dates.
    """

    def add_task(self, uid: task.UID, /) -> None:
        """Add task to register."""
        raise NotImplementedError

    def add_event(self, uid: event.UID, /) -> None:
        """Add event to register."""
        raise NotImplementedError

    def add_dependency(self, task_uid: task.UID, event_uid: event.UID) -> None:
        """Add dependency between task and event."""
        raise NotImplementedError

    def tasks_due_by(self, uid: event.UID) -> TaskUIDsView:
        """Tasks due by the specified event."""
        raise NotImplementedError

    def events_due_by(self, uid: task.UID) -> EventUIDsView:
        """Events a the specified task is due by."""
        raise NotImplementedError

    def dependencies(self) -> Generator[tuple[task.UID, event.UID], None, None]:
        """Return all dependencies."""
        raise NotImplementedError
