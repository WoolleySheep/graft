"""Task Register and associated exceptions."""

import datetime as dt
from collections.abc import Iterator, Mapping, MutableMapping
from typing import Any, Protocol

from graft.domain.event import event


class Register(Mapping[event.UID, event.AttributesView]):
    """Register mapping event UIDs to attributes."""

    def __init__(
        self, uid_to_attributes_map: MutableMapping[event.UID, event.Attributes]
    ) -> None:
        """Initialise Register."""
        self._uid_to_attributes_map = uid_to_attributes_map

    def add(self, /, uid: event.UID) -> None:
        """Add a new event."""
        if uid in self:
            raise event.UIDAlreadyExistsError(uid=uid)

        self._uid_to_attributes_map[uid] = event.Attributes(
            name=None, description=None, datetime=None
        )

    def remove(self, /, uid: event.UID) -> None:
        """Remove an existing event."""
        if uid not in self:
            raise event.UIDDoesNotExistError(uid=uid)

        del self._uid_to_attributes_map[uid]

    def update_name(self, uid: event.UID, name: event.Name | None) -> None:
        """Update name of an existing event."""
        if uid not in self:
            raise event.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].name = name

    def update_description(
        self, uid: event.UID, description: event.Description | None
    ) -> None:
        """Update description of an existing event."""
        if uid not in self:
            raise event.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].description = description

    def update_datetime(self, uid: event.UID, datetime: dt.datetime | None) -> None:
        """Update datetime of an existing event."""
        if uid not in self:
            raise event.UIDDoesNotExistError(uid=uid)

        self._uid_to_attributes_map[uid].datetime = datetime

    def __contains__(self, item: object) -> bool:
        """Check if UID registered."""
        return item in self._uid_to_attributes_map

    def __bool__(self) -> bool:
        """Check if any events registered."""
        return bool(self._uid_to_attributes_map)

    def __getitem__(self, key: event.UID) -> event.AttributesView:
        """Get view of attributes for UID."""
        if key in self._uid_to_attributes_map:
            raise event.UIDDoesNotExistError(uid=key)

        return event.AttributesView(self._uid_to_attributes_map[key])

    def __iter__(self) -> Iterator[event.UID]:
        """Return iterator over event UIDs in register."""
        return iter(self._uid_to_attributes_map)


class RegisterView(Protocol):
    """View-only event register."""

    def __contains__(self, item: object) -> bool:
        """Check if event UID is in register."""
        ...

    def __iter__(self) -> Iterator[event.UID]:
        """Return iterator over eventUIDs in register."""
        ...

    def __len__(self) -> int:
        """Return number of events in the register."""
        ...

    def __getitem__(self, key: event.UID) -> event.AttributesView:
        """Return AttributeView of attributes associated with key."""
        ...
