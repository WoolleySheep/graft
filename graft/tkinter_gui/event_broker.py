import abc
import collections
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
        self.event_callbacks_map = collections.defaultdict[
            Type[Event], list[Callable[[Event], None]]
        ](list)

    def publish(self, event: Event) -> None:
        for callback in self.event_callbacks_map[type(event)]:
            callback(event)

    def subscribe(
        self, event_type: Type[Event], callback: Callable[[Event], None]
    ) -> None:
        self.event_callbacks_map[event_type].append(callback)


_singleton = EventBroker()


def get_singleton() -> EventBroker:
    return _singleton
