"""AttributesRegister and associated classes/exceptions."""

from collections.abc import Iterator, Mapping, MutableMapping

from graft.domain.tasks.attributes import Attributes, AttributesView
from graft.domain.tasks.description import Description
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.name import Name
from graft.domain.tasks.uid import UID


class AttributesRegister(Mapping[UID, AttributesView]):
    """Register mapping task UIDs to attributes."""

    def __init__(self, task_to_attributes_map: MutableMapping[UID, Attributes]) -> None:
        """Initialise Register."""
        self._task_to_attributes_map = task_to_attributes_map

    def __contains__(self, item: object) -> bool:
        """Check if UID registered."""
        return item in self._task_to_attributes_map

    def __iter__(self) -> Iterator[UID]:
        """Iterate over the task UIDs in the register."""
        return iter(self._task_to_attributes_map)

    def __bool__(self) -> bool:
        """Check if any tasks registered."""
        return bool(self._task_to_attributes_map)

    def __len__(self) -> int:
        """Return number of tasks in the register."""
        return len(self._task_to_attributes_map)

    def __getitem__(self, key: UID) -> AttributesView:
        """Get view of attributes for UID."""
        try:
            attributes = self._task_to_attributes_map[key]
        except KeyError as e:
            raise TaskDoesNotExistError(task=key) from e

        return AttributesView(attributes=attributes)

    def add(self, /, task: UID) -> None:
        """Add a new task."""
        if task in self:
            raise TaskAlreadyExistsError(task=task)

        self._task_to_attributes_map[task] = Attributes(name=None, description=None)

    def remove(self, /, task: UID) -> None:
        """Remove an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        del self._task_to_attributes_map[task]

    def update_name(self, task: UID, name: Name | None) -> None:
        """Update name of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task].name = name

    def update_description(self, task: UID, description: Description | None) -> None:
        """Update description of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task].description = description


class AttributesRegisterView(Mapping[UID, AttributesView]):
    """View-only task attributes register."""

    def __init__(self, attributes_register: AttributesRegister) -> None:
        """Initialise AttributesRegisterView."""
        self._attributes_register = attributes_register

    def __contains__(self, item: object) -> bool:
        """Check if task UID is in register."""
        return item in self._attributes_register

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over task UIDs in register."""
        return iter(self._attributes_register)

    def __len__(self) -> int:
        """Return number of tasks in the register."""
        return len(self._attributes_register)

    def __getitem__(self, key: UID) -> AttributesView:
        """Return view of attributes associated with key."""
        return self._attributes_register[key]
