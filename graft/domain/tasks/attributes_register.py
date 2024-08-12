"""AttributesRegister and associated classes/exceptions."""

from collections.abc import Iterator, Mapping
from typing import Protocol

from graft.domain.tasks.attributes import Attributes, AttributesView
from graft.domain.tasks.description import Description
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.uid import UID


class IAttributesRegisterView(Protocol):
    """Interface for a view of an attributes register."""

    def __bool__(self) -> bool:
        """Check if any tasks registered."""
        ...

    def __contains__(self, item: object) -> bool:
        """Check if task UID is in register."""
        ...

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over task UIDs in register."""
        ...

    def __len__(self) -> int:
        """Return number of tasks in the register."""
        ...

    def __getitem__(self, key: UID) -> AttributesView:
        """Return view of attributes associated with key."""
        ...


class AttributesRegister(Mapping[UID, AttributesView]):
    """Register mapping task UIDs to attributes."""

    def __init__(
        self, task_to_attributes_map: Mapping[UID, Attributes] | None = None
    ) -> None:
        """Initialise Register."""
        self._task_to_attributes_map = (
            dict(task_to_attributes_map)
            if task_to_attributes_map
            else dict[UID, Attributes]()
        )

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

    def __eq__(self, other: object) -> bool:
        """Check if two registers are equal."""
        return isinstance(other, AttributesRegister) and dict(self.items()) == dict(
            other.items()
        )

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

        self._task_to_attributes_map[task] = Attributes()

    def remove(self, /, task: UID) -> None:
        """Remove an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        del self._task_to_attributes_map[task]

    def set_name(self, task: UID, name: Name) -> None:
        """Set name of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task] = self._task_to_attributes_map[task].copy(
            name=name
        )

    def set_description(self, task: UID, description: Description) -> None:
        """Set description of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task] = self._task_to_attributes_map[task].copy(
            description=description
        )

    def set_progress(self, task: UID, progress: Progress | None = None) -> None:
        """Set progress of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task] = self._task_to_attributes_map[task].copy(
            progress=progress
        )

    def set_importance(self, task: UID, importance: Importance | None = None) -> None:
        """Set importance of an existing task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        self._task_to_attributes_map[task] = self._task_to_attributes_map[task].copy(
            importance=importance
        )


class AttributesRegisterView(Mapping[UID, AttributesView]):
    """View-only task attributes register."""

    def __init__(self, attributes_register: IAttributesRegisterView) -> None:
        """Initialise AttributesRegisterView."""
        self._attributes_register = attributes_register

    def __bool__(self) -> bool:
        """Check if any tasks registered."""
        return bool(self._attributes_register)

    def __contains__(self, item: object) -> bool:
        """Check if task UID is in register."""
        return item in self._attributes_register

    def __iter__(self) -> Iterator[UID]:
        """Return iterator over task UIDs in register."""
        return iter(self._attributes_register)

    def __len__(self) -> int:
        """Return number of tasks in the register."""
        return len(self._attributes_register)

    def __eq__(self, other: object) -> bool:
        """Check if two register views are equal."""
        return isinstance(other, AttributesRegisterView) and dict(self.items()) == dict(
            other.items()
        )

    def __getitem__(self, key: UID) -> AttributesView:
        """Return view of attributes associated with key."""
        return self._attributes_register[key]
