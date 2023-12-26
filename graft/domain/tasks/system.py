"""System and associated classes/exceptions."""

import collections
from collections.abc import Generator, Iterator

from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import (
    DependencyGraph,
    DependencyGraphView,
    HasDependeeTasksError,
    HasDependentTasksError,
)
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HasSubTasksError,
    HasSuperTasksError,
    HierarchyGraph,
    HierarchyGraphView,
    HierarchyLoopError,
)
from graft.domain.tasks.uid import UID


class System:
    """System of task information."""

    def __init__(
        self,
        attributes_register: AttributesRegister,
        hierarchy_graph: HierarchyGraph,
        dependency_graph: DependencyGraph,
    ) -> None:
        """Initialise System."""
        self._attributes_register = attributes_register
        self._hierarchy_graph = hierarchy_graph
        self._dependency_graph = dependency_graph

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return AttributesRegisterView(self._attributes_register)

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return HierarchyGraphView(self._hierarchy_graph)

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return DependencyGraphView(self._dependency_graph)

    def __bool__(self) -> bool:
        """Return True if the system is not empty."""
        return bool(self._attributes_register)

    def __contains__(self, key: UID) -> bool:
        """Return True if key is in the task network."""
        return key in self._attributes_register

    def __iter__(self) -> Iterator[UID]:
        """Iterate over the task UIDs in the network."""
        return iter(self._attributes_register)

    def downstream_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of downstream tasks of task.

        Because there is two graphs involved (hierarchy and dependency) it is
        impossible to do a true breadth-first search. However, I have attempted
        to approximate this by searching in expanding 'rings', exhausting all of
        the supertasks, subtasks and dependent tasks in each ring before moving
        to the next. That is the reason for the strange double-queue situation.
        """
        check_dependent_tasks_queue = collections.deque[UID]()
        check_subtasks_queue = collections.deque[UID]()
        check_supertasks_queue = collections.deque[UID]()

        check_dependent_tasks_queue2 = collections.deque[UID]()
        check_subtasks_queue2 = collections.deque[UID]()
        check_supertasks_queue2 = collections.deque[UID]()

        visited_dependent_tasks = set[UID]()
        visited_subtasks = set[UID]()
        visited_supertasks = set[UID]()

        yielded_tasks = set[UID]()

        for supertask in self._hierarchy_graph.supertasks(task):
            check_dependent_tasks_queue2.append(supertask)
            check_supertasks_queue2.append(supertask)

        for dependent_task in self._dependency_graph.dependent_tasks(task):
            check_dependent_tasks_queue2.append(dependent_task)
            check_subtasks_queue2.append(dependent_task)
            check_supertasks_queue2.append(dependent_task)

        while (
            check_dependent_tasks_queue2
            or check_subtasks_queue2
            or check_supertasks_queue2
        ):
            check_dependent_tasks_queue, check_dependent_tasks_queue2 = (
                check_dependent_tasks_queue2,
                check_dependent_tasks_queue,
            )
            check_subtasks_queue, check_subtasks_queue2 = (
                check_subtasks_queue2,
                check_subtasks_queue,
            )
            check_supertasks_queue, check_supertasks_queue2 = (
                check_supertasks_queue2,
                check_supertasks_queue,
            )

            while check_dependent_tasks_queue:
                task2 = check_dependent_tasks_queue.popleft()
                if task2 in visited_dependent_tasks:
                    continue
                visited_dependent_tasks.add(task2)
                for dependent_task in self._dependency_graph.dependent_tasks(task2):
                    check_dependent_tasks_queue2.append(dependent_task)
                    check_subtasks_queue2.append(dependent_task)
                    check_supertasks_queue2.append(dependent_task)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while check_subtasks_queue:
                task2 = check_subtasks_queue.popleft()
                if task2 in visited_subtasks:
                    continue
                visited_subtasks.add(task2)
                for subtask in self._hierarchy_graph.subtasks(task2):
                    check_dependent_tasks_queue2.append(subtask)
                    check_subtasks_queue2.append(subtask)
                    check_supertasks_queue2.append(subtask)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while check_supertasks_queue:
                task2 = check_supertasks_queue.popleft()
                if task2 in visited_supertasks:
                    continue
                visited_supertasks.add(task2)
                for dependent_task in self._dependency_graph.dependent_tasks(task2):
                    check_dependent_tasks_queue2.append(dependent_task)
                    check_supertasks_queue2.append(dependent_task)

    def upstream_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of downstream tasks of task.

        Because there is two graphs involved (hierarchy and dependency) it is
        impossible to do a true breadth-first search. However, I have attempted
        to approximate this by searching in expanding 'rings', exhausting all of
        the supertasks, subtasks and dependee tasks in each ring before moving
        to the next. That is the reason for the strange double-queue situation.
        """
        check_dependee_tasks_queue = collections.deque[UID]()
        check_subtasks_queue = collections.deque[UID]()
        check_supertasks_queue = collections.deque[UID]()

        check_dependee_tasks_queue2 = collections.deque[UID]()
        check_subtasks_queue2 = collections.deque[UID]()
        check_supertasks_queue2 = collections.deque[UID]()

        visited_dependee_tasks = set[UID]()
        visited_subtasks = set[UID]()
        visited_supertasks = set[UID]()

        yielded_tasks = set[UID]()

        for supertask in self._hierarchy_graph.supertasks(task):
            check_dependee_tasks_queue2.append(supertask)
            check_supertasks_queue2.append(supertask)

        for dependee_task in self._dependency_graph.dependee_tasks(task):
            check_dependee_tasks_queue2.append(dependee_task)
            check_subtasks_queue2.append(dependee_task)
            check_supertasks_queue2.append(dependee_task)

        while (
            check_dependee_tasks_queue2
            or check_subtasks_queue2
            or check_supertasks_queue2
        ):
            check_dependee_tasks_queue, check_dependee_tasks_queue2 = (
                check_dependee_tasks_queue2,
                check_dependee_tasks_queue,
            )
            check_subtasks_queue, check_subtasks_queue2 = (
                check_subtasks_queue2,
                check_subtasks_queue,
            )
            check_supertasks_queue, check_supertasks_queue2 = (
                check_supertasks_queue2,
                check_supertasks_queue,
            )

            while check_dependee_tasks_queue:
                task2 = check_dependee_tasks_queue.popleft()
                if task2 in visited_dependee_tasks:
                    continue
                visited_dependee_tasks.add(task2)
                for dependee_task in self._dependency_graph.dependee_tasks(task2):
                    check_dependee_tasks_queue2.append(dependee_task)
                    check_subtasks_queue2.append(dependee_task)
                    check_supertasks_queue2.append(dependee_task)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while check_subtasks_queue:
                task2 = check_subtasks_queue.popleft()
                if task2 in visited_subtasks:
                    continue
                visited_subtasks.add(task2)
                for subtask in self._hierarchy_graph.subtasks(task2):
                    check_dependee_tasks_queue2.append(subtask)
                    check_subtasks_queue2.append(subtask)
                    check_supertasks_queue2.append(subtask)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while check_supertasks_queue:
                task2 = check_supertasks_queue.popleft()
                if task2 in visited_supertasks:
                    continue
                visited_supertasks.add(task2)
                for dependee_task in self._dependency_graph.dependee_tasks(task2):
                    check_dependee_tasks_queue2.append(dependee_task)
                    check_supertasks_queue2.append(dependee_task)

    def is_stream_path(self, source_task: UID, target_task: UID) -> bool:
        """Check if there is a path from source to target tasks.

        Same as checking if target task is downstream of source task.
        """
        return target_task in self.downstream_tasks_bfs(source_task)

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        self._attributes_register.add(task)
        self._hierarchy_graph.add_task(task)
        self._dependency_graph.add_task(task)

    def remove_task(self, /, task: UID) -> None:
        """Remove a task."""
        if task not in self:
            raise TaskDoesNotExistError(task=task)

        if supertasks := self._hierarchy_graph.supertasks(task):
            raise HasSuperTasksError(task=task, supertasks=supertasks)

        if subtasks := self._hierarchy_graph.subtasks(task):
            raise HasSubTasksError(task=task, subtasks=subtasks)

        if dependee_tasks := self._dependency_graph.dependee_tasks(task):
            raise HasDependeeTasksError(task=task, dependee_tasks=dependee_tasks)

        if dependent_tasks := self._dependency_graph.dependent_tasks(task):
            raise HasDependentTasksError(task=task, dependent_tasks=dependent_tasks)

        self._attributes_register.remove(task)
        self._hierarchy_graph.remove_task(task)
        self._dependency_graph.remove_task(task)

    def add_hierarchy(self, /, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        if supertask == subtask:
            raise HierarchyLoopError(task=supertask)

        for task in [supertask, subtask]:
            if task not in self:
                raise TaskDoesNotExistError(task=task)

        # TODO: Lots of checks here. Refer to add_hierarchy in
        # hierarchy_graph.py, as well as task_network.py from archive #2

        raise NotImplementedError


class SystemView:
    """View of System."""

    def __init__(self, system: System) -> None:
        """Initialise SystemView."""
        self._system = system

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return self._system.attributes_register_view()

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.hierarchy_graph_view()

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._system.dependency_graph_view()
