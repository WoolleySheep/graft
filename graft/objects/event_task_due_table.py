from typing import Iterable

import graft.objects.event as event
import graft.objects.task as task


class EventTaskDueTable:
    def __init__(self) -> None:
        self._event_task_pairs: list[tuple[event.Id, task.Id]] = []

    def __iter__(self) -> Iterable[tuple[event.Id, task.Id]]:
        return iter(self._event_task_pairs)

    def get_tasks(self, event_id: event.Id) -> Iterable[task.Id]:
        return (
            task_id
            for event_id2, task_id in self._event_task_pairs
            if event_id2 == event_id
        )

    def get_events(self, task_id: task.Id) -> Iterable[event.Id]:
        return (
            event_id
            for event_id, task_id2 in self._event_task_pairs
            if task_id2 == task_id
        )

    def add(self, event_id: event.Id, task_id: task.Id) -> None:
        if (event_id, task_id) in self._event_task_pairs:
            raise ValueError

        self._event_task_pairs.append((event_id, task_id))

    def remove(self, event_id: event.Id, task_id: task.Id) -> None:
        if (event_id, task_id) not in self._event_task_pairs:
            raise ValueError

        self._event_task_pairs.remove((event_id, task_id))
