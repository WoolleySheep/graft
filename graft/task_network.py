import collections
import dataclasses
from typing import Hashable, Mapping, MutableMapping

from graft.constrained_graph import ConstrainedGraph
from graft.priority import Priority
from graft.task_attributes import TaskAttributes


class TaskDoesNotExistError(Exception):
    def __init__(self, uid: str, *args, **kwargs):
        self.uid = uid

        super().__init__(f"task [{uid}] does not exist", *args, **kwargs)


class SuperiorTaskPrioritiesError(Exception):
    def __init__(
        self,
        uid: str,
        task_attributes_map: Mapping[str, TaskAttributes],
        task_hierarchy: ConstrainedGraph,
        *args,
        **kwargs,
    ):
        self.uid = uid
        self.superior_tasks_with_priorities = []

        # TODO: Decide on whether to calculate subgraph instead
        unsearched_tasks = collections.deque(task_hierarchy.predecessors(node=uid))
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            searched_tasks.add(task)
            priority = task_attributes_map[task].priority
            if priority:
                self.superior_tasks_with_priorities.append(task)
                continue

            for supertask in task_hierarchy.predecessors(node=task):
                if supertask not in searched_tasks:
                    unsearched_tasks.append(supertask)

        formatted_superior_tasks_and_priorities = [
            f"[{uid}]: [{task_attributes_map[uid].priority}]"
            for uid in self.superior_tasks_with_priorities
        ]
        superior_tasks_and_priorities_formatted = ", ".join(
            formatted_superior_tasks_and_priorities
        )

        super().__init__(
            f"task [{uid}] has superior tasks with priorities: {superior_tasks_and_priorities_formatted}",
            *args,
            **kwargs,
        )


@dataclasses.dataclass
class TaskNetwork:
    task_attributes_map: MutableMapping[str, TaskAttributes]
    task_hierarchy: ConstrainedGraph
    task_dependencies: ConstrainedGraph

    def set_priority(self, uid: str, priority: Priority) -> None:
        # TODO: Only requires task_attributes_map & task_hierarchy, not task_dependencies. Consider making a new class, or using a function.
        try:
            attributes = self.task_attributes_map[uid]
        except KeyError as e:
            raise TaskDoesNotExistError(uid=uid) from e

        # Don't need to search if task already has a priority
        if not attributes.priority and self._do_any_superior_tasks_have_priority(
            uid=uid
        ):
            raise SuperiorTaskPrioritiesError(
                uid=uid,
                task_attributes_map=self.task_attributes_map,
                task_hierarchy=self.task_hierarchy,
            )

        attributes.priority = priority

    def _do_any_superior_tasks_have_priority(self, uid: str) -> bool:
        """Do any of the superior tasks of task [uid] have a priority?"""
        # Assumption is that task [uid] does not have a set priority
        unsearched_tasks = collections.deque(self.task_hierarchy.predecessors(node=uid))
        searched_tasks = set()
        while unsearched_tasks:
            task = unsearched_tasks.popleft()
            priority = self.task_attributes_map[task].priority
            if priority:
                return True
            searched_tasks.add(task)
            for supertask in self.task_hierarchy.predecessors(node=task):
                if supertask not in searched_tasks:
                    unsearched_tasks.append(supertask)

        return False
