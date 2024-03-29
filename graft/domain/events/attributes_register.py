"""AttributesRegister and associated exceptions."""

import copy
from collections.abc import Iterator, Mapping

from graft.domain.events.attributes import Attributes, AttributesView
from graft.domain.events.description import Description
from graft.domain.events.name import Name
from graft.domain.events.uid import UID, UIDAlreadyExistsError, UIDDoesNotExistError


class AttributesRegister(Mapping[UID, AttributesView]):
    """Register mapping event UIDs to attributes."""

    def __init__(self, event_to_attributes_map: Mapping[UID, Attributes]) -> None:
        """Initialise AttributesRegister."""
        self._event_to_attributes_map = (
            {
                event: copy.deepcopy(attributes)
                for event, attributes in event_to_attributes_map.items()
            }
            if event_to_attributes_map
            else dict[UID, Attributes]()
        )

    def __contains__(self, item: object) -> bool:
        """Check if UID registered."""
        return item in self._event_to_attributes_map

    def __len__(self) -> int:
        """Return number of events in register."""
        return len(self._event_to_attributes_map)

    def __bool__(self) -> bool:
        """Check if any events registered."""
        return bool(self._event_to_attributes_map)

    def __getitem__(self, key: UID) -> AttributesView:
        """Get view of attributes for UID."""
        if key in self._event_to_attributes_map:
            raise UIDDoesNotExistError(uid=key)

        return AttributesView(self._event_to_attributes_map[key])

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over event UIDs in register."""
        return iter(self._event_to_attributes_map)

    def add(self, /, uid: UID) -> None:
        """Add a new event."""
        if uid in self:
            raise UIDAlreadyExistsError(uid=uid)

        self._event_to_attributes_map[uid] = Attributes(name=None, description=None)

    def remove(self, /, uid: UID) -> None:
        """Remove an existing event."""
        if uid not in self:
            raise UIDDoesNotExistError(uid=uid)

        del self._event_to_attributes_map[uid]

    def update_name(self, uid: UID, name: Name | None) -> None:
        """Update name of an existing event."""
        if uid not in self:
            raise UIDDoesNotExistError(uid=uid)

        self._event_to_attributes_map[uid].name = name

    def update_description(self, uid: UID, description: Description | None) -> None:
        """Update description of an existing event."""
        if uid not in self:
            raise UIDDoesNotExistError(uid=uid)

        self._event_to_attributes_map[uid].description = description


class AttributesRegisterView(Mapping[UID, AttributesView]):
    """View-only event attributes register."""

    def __init__(self, attributes_register: AttributesRegister) -> None:
        """Initialise AttributesRegisterView."""
        self._attributes_register = attributes_register

    def __contains__(self, item: object) -> bool:
        """Check if event UID is in register."""
        return item in self._attributes_register

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over eventUIDs in register."""
        return iter(self._attributes_register)

    def __len__(self) -> int:
        """Return number of events in the register."""
        return len(self._attributes_register)

    def __getitem__(self, key: UID) -> AttributesView:
        """Return view of attributes associated with key."""
        return self._attributes_register[key]
