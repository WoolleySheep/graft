"""System and associated classes/exceptions."""

import collections
import itertools
from collections.abc import Generator, Iterator
from typing import Any, Self

from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
)
from graft.domain.tasks.dependency_graph import (
    DependencyAlreadyExistsError,
    DependencyGraph,
    DependencyGraphView,
    DependencyIntroducesCycleError,
    DependencyLoopError,
    HasDependeeTasksError,
    HasDependentTasksError,
    InverseDependencyAlreadyExistsError,
)
from graft.domain.tasks.description import Description
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HasSubTasksError,
    HasSuperTasksError,
    HierarchyAlreadyExistsError,
    HierarchyGraph,
    HierarchyGraphView,
    HierarchyIntroducesCycleError,
    HierarchyLoopError,
    HierarchyPathAlreadyExistsError,
    InverseHierarchyAlreadyExistsError,
    SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError,
)
from graft.domain.tasks.name import Name
from graft.domain.tasks.uid import UID


class StreamPathFromSuperTaskToSubTaskExistsError(Exception):
    """Raised when a stream path from a super-task to a sub-task exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromSuperTaskToSubTask."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Stream path from [{supertask}] to [{subtask}] exists.",
            *args,
            **kwargs,
        )


class StreamPathFromSubTaskToSuperTaskExistsError(Exception):
    """Raised when a stream path from a sub-task to a super-task exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromSubTaskToSuperTaskExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Stream path from [{subtask}] to [{supertask}] exists.",
            *args,
            **kwargs,
        )


class StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError(Exception):
    """Raised when a stream path from a super-task to an inferior task of a sub-task exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Stream path from [{supertask}] to inferior task of [{subtask}] exists.",
            *args,
            **kwargs,
        )


class StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError(Exception):
    """Raised when a stream path from an inferior task of a sub-task to a super-task exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Stream path from inferior task of [{subtask}] to [{supertask}] exists.",
            *args,
            **kwargs,
        )


class HierarchyIntroducesDependencyClashError(Exception):
    """Raised when a dependency-clash would be introduced.

    TODO: This exception is linked to a poorly named and understood condition.
    Improve it when you can.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HierarchyIntroducessubtaskClashError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Hierarchy introduces dependency clash between [{supertask}] and [{subtask}].",
            *args,
            **kwargs,
        )


class HierarchyPathAlreadyExistsFromDependeeTaskToDependentTaskError(Exception):
    """Raised when there is already a hierarchy path from dependee-task to dependent-task."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: HierarchyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HierarchyPathAlreadyExistsError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy path already exists from dependee-task [{dependee_task}] to dependent-task [{dependent_task}].",
            *args,
            **kwargs,
        )


class HierarchyPathAlreadyExistsFromDependentTaskToDependeeTaskError(Exception):
    """Raised when there is already a hierarchy path from dependent-task to dependee-task."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: HierarchyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HierarchyPathAlreadyExistsError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy path already exists between dependent-task [{dependent_task}] to dependee-task [{dependee_task}].",
            *args,
            **kwargs,
        )


class DependencyIntroducesStreamCycleError(Exception):
    """Raised when a dependency introduces a stream cycle."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyIntroducesStreamCycleError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Dependency from dependee-task [{dependee_task}] to dependent-task [{dependent_task}] introduces stream cycle.",
            *args,
            **kwargs,
        )


class StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError(Exception):
    """Raised when a stream path from an inferior task of a dependent task to a dependee task exists."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Stream path from inferior task of dependent-task [{dependent_task}] to dependee-task [{dependee_task}] exists.",
            *args,
            **kwargs,
        )


class StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError(Exception):
    """Raised when a stream path from a dependent-task to an inferior-task of a dependee-task exists."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Stream path from dependent-task [{dependent_task}] to inferior task of dependee-task [{dependee_task}] exists.",
            *args,
            **kwargs,
        )


class DependencyIntroducesHierarchyClashError(Exception):
    """Raised when a dependency introduces a hierarchy clash."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyIntroducesHierarchyClashError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Dependency from dependee-task [{dependee_task}] to dependent-task [{dependent_task}] introduces hierarchy clash.",
            *args,
            **kwargs,
        )


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

    def __bool__(self) -> bool:
        """Return True if the system is not empty."""
        return bool(self._attributes_register)

    def __contains__(self, key: UID) -> bool:
        """Return True if key is in the task system."""
        return key in self._attributes_register

    def __len__(self) -> int:
        """Return the number of tasks in the system."""
        return len(self._attributes_register)

    def __iter__(self) -> Iterator[UID]:
        """Iterate over the task UIDs in the system."""
        return iter(self._attributes_register)

    def __eq__(self, other: object) -> bool:
        """Check if two systems are equal."""
        if not isinstance(other, System):
            return False

        return (
            self.attributes_register_view() == other.attributes_register_view()
            and self.hierarchy_graph_view() == other.hierarchy_graph_view()
            and self.dependency_graph_view() == other.dependency_graph_view()
        )

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return AttributesRegisterView(self._attributes_register)

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return HierarchyGraphView(self._hierarchy_graph)

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return DependencyGraphView(self._dependency_graph)

    def _downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks downstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        dependent_tasks_to_check_queue = collections.deque[UID]()
        subtasks_to_check_queue = collections.deque[UID]()
        supertasks_to_check_queue = collections.deque[UID]()

        visited_dependent_tasks = set[UID]()
        visited_subtasks = set[UID]()
        visited_supertasks = set[UID]()

        yielded_tasks = set[UID]()

        for supertask in self._hierarchy_graph.supertasks(task):
            dependent_tasks_to_check_queue.append(supertask)
            supertasks_to_check_queue.append(supertask)

        for dependent_task in self._dependency_graph.dependent_tasks(task):
            dependent_tasks_to_check_queue.append(dependent_task)
            subtasks_to_check_queue.append(dependent_task)
            supertasks_to_check_queue.append(dependent_task)

        while (
            dependent_tasks_to_check_queue
            or subtasks_to_check_queue
            or supertasks_to_check_queue
        ):
            while dependent_tasks_to_check_queue:
                task2 = dependent_tasks_to_check_queue.popleft()
                if task2 in visited_dependent_tasks:
                    continue
                visited_dependent_tasks.add(task2)
                for dependent_task in self._dependency_graph.dependent_tasks(task2):
                    dependent_tasks_to_check_queue.append(dependent_task)
                    subtasks_to_check_queue.append(dependent_task)
                    supertasks_to_check_queue.append(dependent_task)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while subtasks_to_check_queue:
                task2 = subtasks_to_check_queue.popleft()
                if task2 in visited_subtasks:
                    continue
                visited_subtasks.add(task2)
                for subtask in self._hierarchy_graph.subtasks(task2):
                    dependent_tasks_to_check_queue.append(subtask)
                    subtasks_to_check_queue.append(subtask)
                    supertasks_to_check_queue.append(subtask)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while supertasks_to_check_queue:
                task2 = supertasks_to_check_queue.popleft()
                if task2 in visited_supertasks:
                    continue
                visited_supertasks.add(task2)
                for dependent_task in self._dependency_graph.dependent_tasks(task2):
                    dependent_tasks_to_check_queue.append(dependent_task)
                    supertasks_to_check_queue.append(dependent_task)

    def _upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks upstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        dependee_tasks_to_check_queue = collections.deque[UID]()
        subtasks_to_check_queue = collections.deque[UID]()
        supertasks_to_check_queue = collections.deque[UID]()

        visited_dependee_tasks = set[UID]()
        visited_subtasks = set[UID]()
        visited_supertasks = set[UID]()

        yielded_tasks = set[UID]()

        for supertask in self._hierarchy_graph.supertasks(task):
            dependee_tasks_to_check_queue.append(supertask)
            supertasks_to_check_queue.append(supertask)

        for dependee_task in self._dependency_graph.dependee_tasks(task):
            dependee_tasks_to_check_queue.append(dependee_task)
            subtasks_to_check_queue.append(dependee_task)
            supertasks_to_check_queue.append(dependee_task)

        while (
            dependee_tasks_to_check_queue
            or subtasks_to_check_queue
            or supertasks_to_check_queue
        ):
            while dependee_tasks_to_check_queue:
                task2 = dependee_tasks_to_check_queue.popleft()
                if task2 in visited_dependee_tasks:
                    continue
                visited_dependee_tasks.add(task2)
                for dependee_task in self._dependency_graph.dependee_tasks(task2):
                    dependee_tasks_to_check_queue.append(dependee_task)
                    subtasks_to_check_queue.append(dependee_task)
                    supertasks_to_check_queue.append(dependee_task)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while subtasks_to_check_queue:
                task2 = subtasks_to_check_queue.popleft()
                if task2 in visited_subtasks:
                    continue
                visited_subtasks.add(task2)
                for subtask in self._hierarchy_graph.subtasks(task2):
                    dependee_tasks_to_check_queue.append(subtask)
                    subtasks_to_check_queue.append(subtask)
                    supertasks_to_check_queue.append(subtask)
                if task2 in yielded_tasks:
                    continue
                yielded_tasks.add(task2)
                yield task2

            while supertasks_to_check_queue:
                task2 = supertasks_to_check_queue.popleft()
                if task2 in visited_supertasks:
                    continue
                visited_supertasks.add(task2)
                for dependee_task in self._dependency_graph.dependee_tasks(task2):
                    dependee_tasks_to_check_queue.append(dependee_task)
                    supertasks_to_check_queue.append(dependee_task)

    def _has_stream_path(self, source_task: UID, target_task: UID) -> bool:
        """Check if there is a stream path from source to target tasks.

        Same as checking if target task is downstream of source task.
        """
        return target_task in self._downstream_tasks(source_task)

    def _has_stream_path_from_source_to_inferior_task_of_target(
        self, source_task: UID, target_task: UID
    ) -> bool:
        """Check if there is a stream path from source-task to an inferior task of target-task."""
        inferior_tasks_of_target = set(
            self._hierarchy_graph.inferior_tasks_bfs(target_task)
        )
        return any(
            downstream_task in inferior_tasks_of_target
            for downstream_task in self._downstream_tasks(source_task)
        )

    def _has_stream_path_from_inferior_task_of_source_to_target(
        self, source_task: UID, target_task: UID
    ) -> bool:
        """Check if there is a stream path from an inferior task of source-task to target-task."""
        inferior_tasks_of_source = set(
            self._hierarchy_graph.inferior_tasks_bfs(source_task)
        )
        return any(
            upstream_task in inferior_tasks_of_source
            for upstream_task in self._upstream_tasks(target_task)
        )

    def add_task(self, task: UID, /) -> None:
        """Add a task."""
        self._attributes_register.add(task)
        self._hierarchy_graph.add_task(task)
        self._dependency_graph.add_task(task)

    def remove_task(self, task: UID, /) -> None:
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

    def set_name(self, task: UID, name: Name | None = None) -> None:
        """Set the name of the specified task."""
        self._attributes_register.set_name(task, name)

    def set_description(
        self, task: UID, description: Description | None = None
    ) -> None:
        """Set the description of the specified task."""
        self._attributes_register.set_description(task, description)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""

        def has_dependency_clash(self: Self, supertask: UID, subtask: UID) -> bool:
            """Quite a complicated little check - read the description.

            Check if any of the dependent-linked-tasks of (the super-task or
            superior-tasks of the super-task) and any dependent-linked-tasks of
            (the sub-task or inferior-tasks of the sub-task) are (superior to or
            inferior to or the same) as one another.
            """
            dependency_linked_tasks_of_superior_tasks_of_supertask = set()
            for superior_task in itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks_bfs(supertask)
            ):
                dependency_linked_tasks_of_superior_tasks_of_supertask.update(
                    self._dependency_graph.dependee_tasks(superior_task)
                )
                dependency_linked_tasks_of_superior_tasks_of_supertask.update(
                    self._dependency_graph.dependent_tasks(superior_task)
                )

            superior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask = (
                self._hierarchy_graph.superior_tasks_subgraph_multi(
                    dependency_linked_tasks_of_superior_tasks_of_supertask
                )
            )

            inferior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask = (
                self._hierarchy_graph.inferior_tasks_subgraph_multi(
                    dependency_linked_tasks_of_superior_tasks_of_supertask
                )
            )

            dependency_linked_tasks_of_inferior_tasks_of_subtask = set()
            for inferior_task in itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks_bfs(subtask)
            ):
                dependency_linked_tasks_of_inferior_tasks_of_subtask.update(
                    self._dependency_graph.dependee_tasks(inferior_task)
                )
                dependency_linked_tasks_of_inferior_tasks_of_subtask.update(
                    self._dependency_graph.dependent_tasks(inferior_task)
                )

            return any(
                task
                in superior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask
                or task
                in inferior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask
                for task in dependency_linked_tasks_of_inferior_tasks_of_subtask
            )

        if supertask == subtask:
            raise HierarchyLoopError(task=supertask)

        for task in [supertask, subtask]:
            if task not in self:
                raise TaskDoesNotExistError(task=task)

        if (supertask, subtask) in self._hierarchy_graph.hierarchies():
            raise HierarchyAlreadyExistsError(supertask, subtask)

        if (subtask, supertask) in self._hierarchy_graph.hierarchies():
            raise InverseHierarchyAlreadyExistsError(supertask, subtask)

        if self._hierarchy_graph.has_path(subtask, supertask):
            connecting_subgraph = self._hierarchy_graph.connecting_subgraph(
                subtask, supertask
            )
            raise HierarchyIntroducesCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            )

        if self._hierarchy_graph.has_path(supertask, subtask):
            connecting_subgraph = self._hierarchy_graph.connecting_subgraph(
                supertask, subtask
            )
            raise HierarchyPathAlreadyExistsError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            )

        subtask_supertasks = self._hierarchy_graph.supertasks(subtask)
        if subtask_supertasks and any(
            supertask_superior_task in subtask_supertasks
            for supertask_superior_task in self._hierarchy_graph.superior_tasks_bfs(
                supertask
            )
        ):
            # TODO: Could make more efficient by returning immediately when all
            # of the supertasks of the subtask have been found - no need to keep
            # searching once this has been done
            supertask_superior_tasks_subgraph = (
                self._hierarchy_graph.superior_tasks_subgraph(
                    supertask, stop_condition=lambda task: task in subtask_supertasks
                )
            )
            subtask_supertasks_in_subgraph = (
                supertask
                for supertask in subtask_supertasks
                if supertask in supertask_superior_tasks_subgraph
            )
            subgraph = supertask_superior_tasks_subgraph.inferior_tasks_subgraph_multi(
                subtask_supertasks_in_subgraph
            )

            raise SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError(
                supertask=supertask, subtask=subtask, subgraph=subgraph
            )

        if self._has_stream_path(supertask, subtask):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromSuperTaskToSubTaskExistsError(supertask, subtask)

        if self._has_stream_path(subtask, supertask):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromSubTaskToSuperTaskExistsError(supertask, subtask)

        if self._has_stream_path_from_source_to_inferior_task_of_target(
            supertask, subtask
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromSuperTaskToInferiorTaskOfSubTaskExistsError(
                supertask, subtask
            )

        if self._has_stream_path_from_inferior_task_of_source_to_target(
            subtask, supertask
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromInferiorTaskOfSubTaskToSuperTaskExistsError(
                supertask, subtask
            )

        if has_dependency_clash(self, supertask, subtask):
            # TODO: Get relevant subgraph and return as part of exception
            raise HierarchyIntroducesDependencyClashError(supertask, subtask)

        self._hierarchy_graph.add_hierarchy(supertask, subtask)

    def remove_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Remove the specified hierarchy."""
        self._hierarchy_graph.remove_hierarchy(supertask, subtask)

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Add a dependency between the specified tasks."""

        def has_hierarchy_clash(
            self: Self, dependee_task: UID, dependent_task: UID
        ) -> bool:
            """Quite a complicated little check - read the description.

            Check if any of (the dependee-task or the superior-tasks of the
            dependee-task or the inferior-tasks of the dependee-task) and (the
            dependent-task or the superior-tasks of the dependent-task or the
            inferior-tasks of the dependent-task) are dependency-linked with one
            another.
            """
            dependency_linked_tasks_of_dependee_task_hierarchical_line = set[UID]()
            for task in itertools.chain(
                [dependee_task],
                self._hierarchy_graph.superior_tasks_bfs(dependee_task),
                self._hierarchy_graph.inferior_tasks_bfs(dependee_task),
            ):
                dependee_tasks = self._dependency_graph.dependee_tasks(task)
                dependency_linked_tasks_of_dependee_task_hierarchical_line.update(
                    dependee_tasks
                )
                dependent_tasks = self._dependency_graph.dependent_tasks(task)
                dependency_linked_tasks_of_dependee_task_hierarchical_line.update(
                    dependent_tasks
                )

            dependent_task_hierarchical_line = itertools.chain(
                [dependent_task],
                self._hierarchy_graph.superior_tasks_bfs(dependent_task),
                self._hierarchy_graph.inferior_tasks_bfs(dependent_task),
            )

            return any(
                task in dependency_linked_tasks_of_dependee_task_hierarchical_line
                for task in dependent_task_hierarchical_line
            )

        if dependee_task == dependent_task:
            raise DependencyLoopError(task=dependee_task)

        for task in [dependee_task, dependent_task]:
            if task not in self:
                raise TaskDoesNotExistError(task=task)

        if (dependee_task, dependent_task) in self._dependency_graph.dependencies():
            raise DependencyAlreadyExistsError(dependee_task, dependent_task)

        if (dependent_task, dependee_task) in self._dependency_graph.dependencies():
            raise InverseDependencyAlreadyExistsError(dependent_task, dependee_task)

        if self._dependency_graph.has_path(dependee_task, dependent_task):
            connecting_subgraph = self._dependency_graph.connecting_subgraph(
                dependee_task, dependent_task
            )
            raise DependencyIntroducesCycleError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            )

        if self._hierarchy_graph.has_path(dependee_task, dependent_task):
            connecting_subgraph = self._hierarchy_graph.connecting_subgraph(
                dependee_task, dependent_task
            )
            raise HierarchyPathAlreadyExistsFromDependeeTaskToDependentTaskError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            )

        if self._hierarchy_graph.has_path(dependent_task, dependee_task):
            connecting_subgraph = self._hierarchy_graph.connecting_subgraph(
                dependent_task, dependee_task
            )
            raise HierarchyPathAlreadyExistsFromDependentTaskToDependeeTaskError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            )

        if self._has_stream_path(dependent_task, dependee_task):
            # TODO: Get relevant subgraph and return as part of exception
            raise DependencyIntroducesStreamCycleError(dependee_task, dependent_task)

        if self._has_stream_path_from_inferior_task_of_source_to_target(
            dependent_task, dependee_task
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromInferiorTaskOfDependentTaskToDependeeTaskExistsError(
                dependee_task, dependent_task
            )

        if self._has_stream_path_from_source_to_inferior_task_of_target(
            dependent_task, dependee_task
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromDependentTaskToInferiorTaskOfDependeeTaskExistsError(
                dependee_task, dependent_task
            )

        if has_hierarchy_clash(
            self, dependee_task=dependee_task, dependent_task=dependent_task
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise DependencyIntroducesHierarchyClashError(dependee_task, dependent_task)

        self._dependency_graph.add_dependency(dependee_task, dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the specified dependency."""
        self._dependency_graph.remove_dependency(dependee_task, dependent_task)


class SystemView:
    """View of System."""

    def __init__(self, system: System) -> None:
        """Initialise SystemView."""
        self._system = system

    def __len__(self) -> int:
        """Return number of tasks in system."""
        return len(self._system)

    def __eq__(self, other: object) -> bool:
        """Check if system views are equal."""
        if not isinstance(other, SystemView):
            return False

        return (
            self.attributes_register_view() == other.attributes_register_view()
            and self.hierarchy_graph_view() == other.hierarchy_graph_view()
            and self.dependency_graph_view() == other.dependency_graph_view()
        )

    def attributes_register_view(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return self._system.attributes_register_view()

    def hierarchy_graph_view(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.hierarchy_graph_view()

    def dependency_graph_view(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._system.dependency_graph_view()
