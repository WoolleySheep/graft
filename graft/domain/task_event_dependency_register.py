from collections.abc import Generator

from graft.domain import events, tasks


class TaskEventDependencyRegister:
    """Dependencies between tasks and events.

    For now this only captures tasks and the events they're due by. Eventually,
    tasks will also be able to use events as start-after dates.
    """

    def add_task(self, task: tasks.UID, /) -> None:
        """Add task to register."""
        raise NotImplementedError

    def add_event(self, event: events.UID, /) -> None:
        """Add event to register."""
        raise NotImplementedError

    def add_dependency(self, task: tasks.UID, event: events.UID) -> None:
        """Add dependency between task and event."""
        raise NotImplementedError

    def tasks_due_by(self, event: events.UID) -> tasks.UIDsView:
        """Tasks due by the specified event."""
        raise NotImplementedError

    def events_due_by(self, task: tasks.UID) -> events.UIDsView:
        """Events a the specified task is due by."""
        raise NotImplementedError

    def dependencies(self) -> Generator[tuple[tasks.UID, events.UID], None, None]:
        """Return all dependencies."""
        raise NotImplementedError
