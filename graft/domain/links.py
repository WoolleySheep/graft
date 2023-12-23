from collections.abc import Iterator, Set

from graft import graph
from graft.domain import event, task


class EventUIDsView(Set[event.UID]):
    """View of a set of event UIDs."""

    def __init__(self, events: Set[event.UID], /) -> None:
        """Initialise EventUIDsView."""
        self._events: Set[event.UID] = events

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


class Links:
    """Links between tasks and events."""

    def tasks_due_by(self, uid: event.UID) -> TaskUIDsView:
        """Tasks due by the specified event."""
        raise NotImplementedError

    def events_due_by(self, uid: task.UID) -> EventUIDsView:
        """Events a the specified task is due by."""
        raise NotImplementedError
