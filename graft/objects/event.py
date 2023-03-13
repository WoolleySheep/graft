from __future__ import annotations

import dataclasses
import datetime
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


@dataclasses.dataclass
class Event:
    name: Name | None = None
    description: Description | None = None
    datetime: datetime.datetime | None = None

    @classmethod
    def from_serialisable_format(cls, serialised: dict) -> Event:
        name = serialised["name"]
        if name is not None:
            name = Name(name)

        description = serialised["description"]
        if description is not None:
            description = Description(description)

        event_datetime = serialised["datetime"]
        if event_datetime is not None:
            event_datetime = datetime.datetime.strptime(
                event_datetime, "%Y-%m-%d %H:%M:%S"
            )

        return cls(name=name, description=description, datetime=event_datetime)

    def to_serialisable_format(self) -> dict[str, Any]:
        return {
            "name": str(self.name) or None,
            "description": str(self.description) or None,
            "datetime": self.datetime.strftime("%Y-%m-%d %H:%M:%S")
            if self.datetime
            else None,
        }


class EventRegister(dict):
    def __contains__(self, id: Id) -> bool:
        return super().__contains__(id)

    def __getitem__(self, id: Id) -> Event:
        return super().__getitem__(id)

    def __setitem__(self, id: Id, event: Event) -> None:
        if id in self:
            raise ValueError

        return super().__setitem__(id, event)

    def __delitem__(self, id: Id) -> None:
        return super().__delitem__(id)
