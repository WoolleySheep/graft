import dataclasses
from typing import Iterable


class TaskTagPairExistsError(Exception):
    def __init__(self, task_uid: str, tag_name: str, *args, **kwargs):
        self.task_uid = task_uid
        self.tag_name = tag_name

        super().__init__(
            f"task [{task_uid}] - tag [{tag_name}] exists", *args, **kwargs
        )


class TaskTagPairDoesNotExistError(Exception):
    def __init__(self, task_uid, tag_name, *args, **kwargs):
        self.task_uid = task_uid
        self.tag_name = tag_name

        super().__init__(
            f"task [{task_uid}] - tag [{tag_name}] does not exist", *args, **kwargs
        )


@dataclasses.dataclass
class TaskTagTable:
    data: set[tuple[str, str]] = dataclasses.field(default_factory=set)

    def get_tags_for_a_task(self, uid: str) -> Iterable[str]:
        """Get all tags for a task"""
        return (tag for task, tag in self.data if task == uid)

    def get_tasks_for_a_tag(self, name: str) -> Iterable[str]:
        """Get all tasks for a tag"""
        return (task for task, tag in self.data if tag == name)

    def does_task_tag_pair_exist(self, task_uid: str, tag_name: str) -> bool:
        return any(task == task_uid and tag == tag_name for task, tag in self.data)

    def add_task_tag_pair(self, task_uid: str, tag_name: str) -> None:
        if self.does_task_tag_pair_exist(task_uid=task_uid, tag_name=tag_name):
            raise TaskTagPairExistsError(task_uid=task_uid, tag_name=tag_name)
        self.data.add((task_uid, tag_name))

    def remove_task_tag_pair(self, task_uid: str, tag_name: str) -> None:
        try:
            self.data.remove((task_uid, tag_name))
        except KeyError:
            raise TaskTagPairDoesNotExistError(task_uid=task_uid, tag_name=tag_name)

    def rename_tag(self, old_name: str, new_name: str) -> None:
        for task, tag in self.data:
            if tag == old_name:
                self.data.remove((task, old_name))
                self.data.add((task, new_name))

    def remove_task(self, uid: str) -> None:
        for task, tag in self.data:
            if task == uid:
                self.data.remove((task, tag))

    def remove_tag(self, name: str) -> None:
        for task, tag in self.data:
            if tag == name:
                self.data.remove((task, tag))

    def is_task_present(self, uid: str) -> bool:
        return any(task == uid for task, _ in self.data)

    def is_tag_present(self, name: str) -> bool:
        return any(tag == name for _, tag in self.data)
