import abc
import collections
import logging
from collections.abc import Callable
from typing import Self

from graft.domain import tasks

logger = logging.getLogger(__name__)


class Event(abc.ABC):
    def __eq__(self, other: object) -> bool:
        # TODO: Work out why this is like this, and if it can be deleted without
        # breaking things
        return isinstance(other, Self)


class SystemModified(Event):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


class TaskSelected(Event):
    def __init__(self, task: tasks.UID) -> None:
        super().__init__()
        self._task = task

    @property
    def task(self) -> tasks.UID:
        return self._task

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.task})"


class EventBroker:
    def __init__(self) -> None:
        logger.info("Initialising %s", self.__class__.__name__)
        self.event_callbacks_map = collections.defaultdict[
            type[Event], list[Callable[[Event], None]]
        ](list)
        logger.info("Initialised %s", self.__class__.__name__)

    def publish(self, event: Event) -> None:
        logger.debug("Event published [%s]", event)
        for callback in self.event_callbacks_map[type(event)]:
            callback(event)

    def subscribe(
        self, event_type: type[Event], callback: Callable[[Event], None]
    ) -> None:
        self.event_callbacks_map[event_type].append(callback)


_singleton = EventBroker()


def get_singleton() -> EventBroker:
    return _singleton
