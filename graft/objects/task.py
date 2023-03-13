from __future__ import annotations

import dataclasses
import enum
from collections import UserString
from typing import Any

_MAX_NAME_LENGTH = 20
_MAX_DESCRIPTION_LENGTH = 100


class Id(UserString):
    def __init__(self, number: int | str) -> None:
        if isinstance(number, str):
            if not number.isdigit():
                raise ValueError
            number = int(number)

        if number < 0:
            raise ValueError

        super().__init__(number)

    def next(self) -> Id:
        return Id(int(self) + 1)


class Name(UserString):
    def __init__(self, text: str) -> None:
        if not (0 < len(text) <= _MAX_NAME_LENGTH):
            raise ValueError

        super().__init__(text)


class Description(UserString):
    def __init__(self, text: str) -> None:
        if not (0 < len(text) <= _MAX_DESCRIPTION_LENGTH):
            raise ValueError

        super().__init__(text)


_OPTIONAL = "optional"
_LOW = "low"
_MEDIUM = "medium"
_HIGH = "high"
_CRITICAL = "critical"

_PRIORITY_ORDER_MAP = {
    _OPTIONAL: 0,
    _LOW: 1,
    _MEDIUM: 2,
    _HIGH: 3,
    _CRITICAL: 4,
}


class Importance(enum.Enum):
    OPTIONAL = _OPTIONAL
    LOW = _LOW
    MEDIUM = _MEDIUM
    HIGH = _HIGH
    CRITICAL = _CRITICAL

    def __lt__(self, other: Importance) -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _PRIORITY_ORDER_MAP[self.value] < _PRIORITY_ORDER_MAP[other.value]

    def __gt__(self, other: Importance) -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError
        return _PRIORITY_ORDER_MAP[self.value] > _PRIORITY_ORDER_MAP[other.value]


_NOT_STARTED = "not started"
_IN_PROGRESS = "in progress"
_COMPLETED = "completed"

_PROGRESS_ORDER_MAP = {_NOT_STARTED: 0, _IN_PROGRESS: 1, _COMPLETED: 3}


class Progress(enum.Enum):
    NOT_STARTED = _NOT_STARTED
    IN_PROGRESS = _IN_PROGRESS
    COMPLETED = _COMPLETED

    def __lt__(self, other: Progress) -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError

        return _PROGRESS_ORDER_MAP[self.value] < _PROGRESS_ORDER_MAP[other.value]

    def __gt__(self, other: Progress) -> bool:
        if self.__class__ is not other.__class__:
            raise NotImplementedError

        return _PROGRESS_ORDER_MAP[self.value] > _PROGRESS_ORDER_MAP[other.value]


@dataclasses.dataclass
class Task:
    name: Name | None = None
    description: Description | None = None
    importance: Importance | None = None
    progress: Progress = Progress.NOT_STARTED

    @classmethod
    def from_serialisable_format(cls, serialised: dict) -> Task:
        name = serialised["name"]
        if name is not None:
            name = Name(name)

        description = serialised["description"]
        if description is not None:
            description = Description(description)

        importance = serialised["importance"]
        if importance is not None:
            importance = Importance(importance)

        progress = Progress(serialised["progress"])

        return cls(
            name=name, description=description, importance=importance, progress=progress
        )

    def to_serialisable_format(self) -> dict[str, Any]:
        return {
            "name": str(self.name) or None,
            "description": str(self.description) or None,
            "importance": self.importance.value if self.importance else None,
            "progress": self.progress.value,
        }


class TaskRegister(dict):
    def __contains__(self, id: Id) -> bool:
        return super().__contains__(id)

    def __getitem__(self, id: Id) -> Task:
        return super().__getitem__(id)

    def __setitem__(self, id: Id, task: Task) -> None:
        if id in self:
            raise ValueError

        return super().__setitem__(id, task)

    def __delitem__(self, id: Id) -> None:
        return super().__delitem__(id)
