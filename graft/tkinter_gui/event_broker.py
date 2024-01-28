import abc
import contextlib
from collections.abc import Callable
from typing import Self, Type

from graft.domain import tasks


class Event(abc.ABC):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Self)


class SystemModified(Event):
    ...


class TaskSelected(Event):
    def __init__(self, task: tasks.UID) -> None:
        super().__init__()
        self.task = task


class EventBroker:
    def __init__(self) -> None:
        self.event_callbacks_map = dict[Type[Event], list[Callable[[Event], None]]]()

    def publish(self, event: Event) -> None:
        with contextlib.suppress(KeyError):
            for callback in self.event_callbacks_map[type(event)]:
                callback(event)

    def subscribe(
        self, event_type: Type[Event], callback: Callable[[Event], None]
    ) -> None:
        if event_type not in self.event_callbacks_map:
            self.event_callbacks_map[event_type] = []

        self.event_callbacks_map[event_type].append(callback)


_singleton = EventBroker()


def get_singleton() -> EventBroker:
    return _singleton
