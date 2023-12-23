"""Task Register and associated exceptions."""

from collections.abc import Iterator, Mapping, MutableMapping
from typing import Protocol

from graft.domain.task import task


class Register(Mapping[task.UID, task.AttributesView]):
    """Register mapping task UIDs to attributes."""

    def __init__(
        self, uid_to_attributes_map: MutableMapping[task.UID, task.Attributes]
    ) -> None:
        """Initialise Register."""
        self._uid_to_attributes_map = uid_to_attributes_map

    def __contains__(self, item: object) -> bool:
        """Check if UID registered."""
        return item in self._uid_to_attributes_map

    def __iter__(self) -> Iterator[task.UID]:
        """Iterate over the task UIDs in the register."""
        return iter(self._uid_to_attributes_map)

    def __bool__(self) -> bool:
        """Check if any tasks registered."""
        return bool(self._uid_to_attributes_map)

    def __getitem__(self, key: task.UID) -> task.AttributesView:
        """Get view of attributes for UID."""
        if key in self._uid_to_attributes_map:
            raise task.UIDDoesNotExistError(uid=key)

        return task.AttributesView(self._uid_to_attributes_map[key])

    def add(self, /, uid: task.UID) -> None:
        """Add a new task."""
        if uid in self:
            raise task.UIDAlreadyExistsError(uid=uid)

        self._uid_to_attributes_map[uid] = task.Attributes(
            name=None, description=None, importance=None
        )

    def remove(self, /, uid: task.UID) -> None:
        """Remove an existing task."""
        if uid not in self:
            raise task.UIDDoesNotExistError(uid=uid)

        del self._uid_to_attributes_map[uid]

    def update_name(self, uid: task.UID, name: task.Name | None) -> None:
        """Update name of an existing task."""
        if uid not in self:
            raise task.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].name = name

    def update_description(
        self, uid: task.UID, description: task.Description | None
    ) -> None:
        """Update description of an existing task."""
        if uid not in self:
            raise task.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].description = description

    def update_importance(
        self, uid: task.UID, importance: task.Importance | None
    ) -> None:
        """Update importance of an existing task."""
        if uid not in self:
            raise task.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].importance = importance


class RegisterView(Protocol):
    """View-only task register."""

    def __contains__(self, item: object) -> bool:
        """Check if task UID is in register."""
        ...

    def __iter__(self) -> Iterator[task.UID]:
        """Return iterator over task UIDs in register."""
        ...

    def __len__(self) -> int:
        """Return number of tasks in the register."""
        ...

    def __getitem__(self, key: task.UID) -> task.AttributesView:
        """Return AttributeView of attributes associated with key."""
        ...
