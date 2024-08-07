"""System and associated classes/exceptions."""

from __future__ import annotations

import collections
import itertools
from collections.abc import Generator, Iterable, Iterator
from typing import Any, Protocol, Self

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
from graft.domain.tasks.description import Description
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HasSubTasksError,
    HasSuperTasksError,
    HierarchyGraph,
    HierarchyGraphView,
)
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.name import Name
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.uid import UID


class DependencyPathAlreadyExistsFromSuperTaskToSubTaskError(Exception):
    """Raised when there is already a dependency path from supertask to subtask."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: DependencyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyPathAlreadyExistsFromSuperTaskToSubTaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency path already exists from supertask [{supertask}] to subtask [{subtask}].",
            *args,
            **kwargs,
        )


class DependencyPathAlreadyExistsFromSubTaskToSuperTaskError(Exception):
    """Raised when there is already a dependency path from supertask to subtask."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: DependencyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyPathAlreadyExistsFromSubTaskToSuperTaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency path already exists from subtask [{subtask}] to supertask [{supertask}].",
            *args,
            **kwargs,
        )


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


class NoConnectingSubsystemError(Exception):
    """Raised when there is no connecting subsystem between two tasks."""

    def __init__(
        self,
        source_task: UID,
        target_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NoConnectingSubsystemError."""
        self.source_task = source_task
        self.target_task = target_task
        super().__init__(
            f"No connecting subsystem between tasks [{source_task}] and [{target_task}].",
            *args,
            **kwargs,
        )


class MultipleImportancesInHierarchyError(Exception):
    """Raised when there are multiple importances in a hierarchy."""

    def __init__(
        self,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise MultipleImportanceInHierarchyError."""
        super().__init__(
            "Multiple importances in hierarchy.",
            *args,
            **kwargs,
        )


class NotConcreteTaskError(Exception):
    """Raised when a task is not concrete, and therefore has no explicit progress."""

    def __init__(
        self, task: UID, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """Initialise NotConcreteTaskError."""
        self.task = task
        super().__init__(f"Task [{task}] is not concrete.", *args, **kwargs)


class ConcreteTaskError(Exception):
    """Raised when a task is concrete, and therefore has no inferred progress."""

    def __init__(
        self, task: UID, *args: tuple[Any, ...], **kwargs: dict[str, Any]
    ) -> None:
        """Initialise ConcreteTaskError."""
        self.task = task
        super().__init__(f"Task [{task}] is concrete.", *args, **kwargs)


class StartedDependentTasksError(Exception):
    """Raised when a task has started dependent tasks.

    Task cannot be uncompleted, as dependent tasks depend on it being completed.
    """

    def __init__(
        self,
        task: UID,
        started_dependent_tasks_with_progress: Iterable[tuple[UID, Progress]],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StartedDependentTasksError."""
        self.task = task
        self.dependee_tasks_with_progress = list(started_dependent_tasks_with_progress)
        super().__init__(f"Task [{task}] has started dependent tasks.", *args, **kwargs)


class StartedDependentTasksOfSuperiorTasksError(Exception):
    """Raised when a task has started dependent tasks of superior tasks.

    Task cannot be uncompleted, as dependent tasks depend on it being completed.
    """

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StartedDependentTasksOfSuperiorTasksError."""
        self.task = task
        super().__init__(
            f"Task [{task}] has started dependent tasks of superior tasks.",
            *args,
            **kwargs,
        )


class IncompleteDependeeTasksError(Exception):
    """Raised when a task has not incomplete dependee tasks.

    Task cannot be started, as dependee tasks must be completed before the task can be started.
    """

    def __init__(
        self,
        task: UID,
        incomplete_dependee_tasks_with_progress: Iterable[tuple[UID, Progress]],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NotCompletedDependeeTasksError."""
        self.task = task
        self.incomplete_dependee_tasks_with_progress = list(
            incomplete_dependee_tasks_with_progress
        )
        super().__init__(
            f"Task [{task}] has incomplete dependee tasks.", *args, **kwargs
        )


class IncompleteDependeeTasksOfSuperiorTasksError(Exception):
    """Raised when a task has incomplete dependee tasks of superior tasks.

    Task cannot be started, as dependee tasks must be completed before the task can be started.
    """

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NotCompletedDependeeTasksOfSuperiorTasksError."""
        self.task = task
        super().__init__(
            f"Task [{task}] has incomplete dependee tasks of superior tasks.",
            *args,
            **kwargs,
        )


class IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError(Exception):
    """Raised when a supertask has incomplete dependee tasks of superior tasks.

    Started subtask cannot be connected, as dependee tasks must be completed
    before the task can be started.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subtask_progress: Progress,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NotCompletedDependeeTasksOfSuperiorTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subtask_progress = subtask_progress
        super().__init__(
            f"Supertask [{supertask}] has incomplete dependee tasks of superior tasks.",
            *args,
            **kwargs,
        )


class StartedDependentTasksOfSuperiorTasksOfSupertaskError(Exception):
    """Raised when a supertask has started dependent tasks of superior tasks.

    Incomplete subtask cannot be connected, as dependent tasks depend on it being completed.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subtask_progress: Progress,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StartedDependentTasksOfSuperiorTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subtask_progress = subtask_progress
        super().__init__(
            f"Supertask [{supertask}] has started dependent tasks of superior tasks.",
            *args,
            **kwargs,
        )


class IncompleteDependeeTasksOfSupertaskError(Exception):
    """Raised when a supertask has incomplete dependee tasks.

    Started subtask cannot be connected, as dependee tasks must be completed
    before the subtask can be started.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        incomplete_dependee_tasks_of_supertask_with_progress: Iterable[
            tuple[UID, Progress]
        ],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise IncompleteDependeeTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.incomplete_dependee_tasks_of_supertask_with_progress = list(
            incomplete_dependee_tasks_of_supertask_with_progress
        )
        super().__init__(
            f"Supertask [{supertask}] has incomplete dependee tasks.", *args, **kwargs
        )


class StartedDependentTasksOfSupertaskError(Exception):
    """Raised when a supertask has started dependent tasks.

    Incomplete subtask cannot be connected, as dependent tasks depend on it
    being completed.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        started_dependent_tasks_of_supertask_with_progress: Iterable[
            tuple[UID, Progress]
        ],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StartedDependentTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.started_dependent_tasks_of_supertask_with_progress = list(
            started_dependent_tasks_of_supertask_with_progress
        )
        super().__init__(
            f"Supertask [{supertask}] has started dependent tasks.", *args, **kwargs
        )


class MismatchedProgressForNewSupertaskError(Exception):
    """Raised when a new supertask has a progress different from its subtask.

    When transforming a concrete task into a non-concrete task by establishing a
    hierarchy, it is important that the progress of the supertask remains the
    same. This means that the progress of any dependent or superior tasks will
    also be unaffected.
    """

    def __init__(
        self,
        supertask: UID,
        supertask_progress: Progress,
        subtask: UID,
        subtask_progress: Progress,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise MismatchedProgressForNewSupertaskError."""
        self.supertask = supertask
        self.supertask_progress = supertask_progress
        self.subtask = subtask
        self.subtask_progress = subtask_progress
        super().__init__(
            f"The progress [{supertask_progress}] of supertask [{supertask}] does not match the progress [{subtask_progress}] of subtask [{subtask}].",
            *args,
            **kwargs,
        )


class DependeeIncompleteDependentStartedError(Exception):
    """Raised when a dependee task is incomplete and a dependent task is started.

    The dependee task cannot be incomplete, as the started dependent task depends on it being complete.
    """

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        dependee_progress: Progress,
        dependent_progress: Progress,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependeeIncompleteDependentStartedError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.dependee_progress = dependee_progress
        self.dependent_progress = dependent_progress
        super().__init__(
            f"Dependee task [{dependee_task}] is [{dependee_progress}] and dependent task [{dependent_task}] is [{dependent_progress}].",
            *args,
            **kwargs,
        )


class SupertaskHasImportanceError(Exception):
    """Raised when a supertask has an importance."""

    def __init__(
        self,
        task: UID,
        supertasks_with_importance: Iterable[tuple[UID, Importance]],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise SupertaskHasImportanceError."""
        self.task = task
        self.supertasks_with_importance = list(supertasks_with_importance)
        super().__init__(
            f"Task [{task}] has supertasks with importance", *args, **kwargs
        )


class SuperiorTaskHasImportanceError(Exception):
    """Raised when a superior task has an importance."""

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise SuperiorTaskHasImportanceError."""
        self.task = task
        super().__init__(
            f"Task [{task}] has superior tasks with importance", *args, **kwargs
        )


class SubtaskHasImportanceError(Exception):
    """Raised when a subtask has an importance."""

    def __init__(
        self,
        task: UID,
        subtasks_with_importance: Iterable[tuple[UID, Importance]],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise SubtaskHasImportanceError."""
        self.task = task
        self.subtasks_with_importance = list(subtasks_with_importance)
        super().__init__(f"Task [{task}] has subtasks with importance", *args, **kwargs)


class InferiorTaskHasImportanceError(Exception):
    """Raised when a inferior task has an importance."""

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise InferiorTaskHasImportanceError."""
        self.task = task
        super().__init__(
            f"Task [{task}] has inferior tasks with importance", *args, **kwargs
        )


class ISystemView(Protocol):
    """Interface for a view of a task system."""

    def __bool__(self) -> bool:
        """Check if there are any tasks in the system."""
        ...

    def __len__(self) -> int:
        """Return number of tasks in system."""
        ...

    def __iter__(self) -> Iterator[UID]:
        """Return an iterator over the tasks in the system."""
        ...

    def __contains__(self, task: UID) -> bool:
        """Check if the specified task exists in the system."""
        ...

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        ...

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        ...

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        ...

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        ...

    def get_importance(self, task: UID, /) -> Importance | set[Importance] | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance.
        """
        ...


class System:
    """System of task information."""

    @classmethod
    def empty(cls) -> System:
        """Create an empty System."""
        return cls(
            attributes_register=AttributesRegister(),
            hierarchy_graph=HierarchyGraph(),
            dependency_graph=DependencyGraph(),
        )

    def __init__(
        self,
        attributes_register: AttributesRegister,
        hierarchy_graph: HierarchyGraph,
        dependency_graph: DependencyGraph,
    ) -> None:
        """Initialise System."""
        # TODO: Add input validation
        self._attributes_register = attributes_register
        self._hierarchy_graph = hierarchy_graph
        self._dependency_graph = dependency_graph

    def __bool__(self) -> bool:
        """Return True if the system is not empty."""
        return bool(self._attributes_register)

    def __contains__(self, task: UID) -> bool:
        """Return True if key is in the task system."""
        return task in self._attributes_register

    def __len__(self) -> int:
        """Return the number of tasks in the system."""
        return len(self._attributes_register)

    def __iter__(self) -> Iterator[UID]:
        """Iterate over the task UIDs in the system."""
        return iter(self._attributes_register)

    def __eq__(self, other: object) -> bool:
        """Check if two systems are equal."""
        return (
            isinstance(other, System)
            and self.attributes_register() == other.attributes_register()
            and self.hierarchy_graph() == other.hierarchy_graph()
            and self.dependency_graph() == other.dependency_graph()
        )

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return AttributesRegisterView(self._attributes_register)

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return HierarchyGraphView(self._hierarchy_graph)

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return DependencyGraphView(self._dependency_graph)

    def _downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks downstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        downstream_tasks_to_check = collections.deque(
            self._dependency_graph.dependent_tasks(task)
        )
        supertasks_to_check = collections.deque(self._hierarchy_graph.supertasks(task))

        visited_downstream_tasks = set[UID]()
        visited_supertasks = set[UID]()

        while downstream_tasks_to_check or supertasks_to_check:
            while downstream_tasks_to_check:
                downstream_task = downstream_tasks_to_check.popleft()
                if downstream_task in visited_downstream_tasks:
                    continue
                yield downstream_task

                visited_downstream_tasks.add(downstream_task)
                downstream_tasks_to_check.extend(
                    itertools.chain(
                        self._dependency_graph.dependent_tasks(downstream_task),
                        self._hierarchy_graph.subtasks(downstream_task),
                    )
                )
                supertasks_to_check.extend(
                    self._hierarchy_graph.supertasks(downstream_task)
                )

            while supertasks_to_check:
                supertask = supertasks_to_check.popleft()
                if supertask in visited_supertasks:
                    continue
                visited_supertasks.add(supertask)
                supertasks_to_check.extend(self._hierarchy_graph.supertasks(supertask))
                downstream_tasks_to_check.extend(
                    self._dependency_graph.dependent_tasks(supertask)
                )

    def _upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks upstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        upstream_tasks_to_check = collections.deque(
            self._dependency_graph.dependee_tasks(task)
        )
        supertasks_to_check = collections.deque[UID](
            self._hierarchy_graph.supertasks(task)
        )

        visited_upstream_tasks = set[UID]()
        visited_supertasks = set[UID]()

        while upstream_tasks_to_check or supertasks_to_check:
            while upstream_tasks_to_check:
                task2 = upstream_tasks_to_check.popleft()
                if task2 in visited_upstream_tasks:
                    continue
                yield task2

                visited_upstream_tasks.add(task2)
                upstream_tasks_to_check.extend(
                    itertools.chain(
                        self._dependency_graph.dependee_tasks(task2),
                        self._hierarchy_graph.subtasks(task2),
                    )
                )
                supertasks_to_check.extend(self._hierarchy_graph.supertasks(task2))

            while supertasks_to_check:
                supertask = supertasks_to_check.popleft()
                if supertask in visited_supertasks:
                    continue
                visited_supertasks.add(supertask)
                supertasks_to_check.extend(self._hierarchy_graph.supertasks(supertask))
                upstream_tasks_to_check.extend(
                    self._dependency_graph.dependee_tasks(supertask)
                )

    def _has_stream_path(self, source_task: UID, target_task: UID) -> bool:
        """Check if there is a stream path from source to target tasks.

        Same as checking if target task is downstream of source task. If the
        source task and the target task are the same, this function will return
        True.
        """
        for task in [source_task, target_task]:
            if task not in self:
                raise TaskDoesNotExistError(task)

        if source_task == target_task:
            return True

        return target_task in self._downstream_tasks(source_task)

    def downstream_subsystem(self, task: UID, /) -> tuple[System, set[UID]]:
        """Return sub-system of all downstream tasks of task.

        Note that the sub-system will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        system = System.empty()
        system.add_task(task)

        downstream_tasks = set[UID]([task])
        non_downstream_tasks = set[UID]()

        tasks_with_dependents_to_check = collections.deque[UID]([task])
        tasks_with_supertasks_to_check = collections.deque[UID]([task])
        tasks_with_subtasks_to_check = collections.deque[UID]()

        tasks_with_checked_dependents = set[UID]()
        tasks_with_checked_subtasks = set[UID]()
        tasks_with_checked_supertasks = set[UID]()

        while (
            tasks_with_dependents_to_check
            or tasks_with_subtasks_to_check
            or tasks_with_supertasks_to_check
        ):
            while tasks_with_dependents_to_check:
                task_with_dependents_to_check = tasks_with_dependents_to_check.popleft()

                if task_with_dependents_to_check in tasks_with_checked_dependents:
                    continue
                tasks_with_checked_dependents.add(task_with_dependents_to_check)

                for dependent_task in self._dependency_graph.dependent_tasks(
                    task_with_dependents_to_check
                ):
                    downstream_tasks.add(dependent_task)
                    tasks_with_dependents_to_check.append(dependent_task)
                    tasks_with_subtasks_to_check.append(dependent_task)
                    tasks_with_supertasks_to_check.append(dependent_task)

                    if dependent_task not in system:
                        system.add_task(dependent_task)
                    system.add_dependency(task_with_dependents_to_check, dependent_task)

        while tasks_with_subtasks_to_check:
            task_with_subtasks_to_check = tasks_with_subtasks_to_check.popleft()

            if task_with_subtasks_to_check in tasks_with_checked_subtasks:
                continue
            tasks_with_checked_subtasks.add(task_with_subtasks_to_check)

            for subtask in self._hierarchy_graph.subtasks(task_with_subtasks_to_check):
                downstream_tasks.add(subtask)
                tasks_with_dependents_to_check.append(subtask)
                tasks_with_subtasks_to_check.append(subtask)
                tasks_with_supertasks_to_check.append(subtask)

                if task not in system:
                    system.add_task(subtask)
                system.add_hierarchy(task_with_subtasks_to_check, subtask)

        while tasks_with_supertasks_to_check:
            task_with_supertasks_to_check = tasks_with_supertasks_to_check.popleft()

            if task_with_supertasks_to_check in tasks_with_checked_supertasks:
                continue
            tasks_with_checked_supertasks.add(task_with_supertasks_to_check)

            for supertask in self._hierarchy_graph.supertasks(
                task_with_supertasks_to_check
            ):
                non_downstream_tasks.add(supertask)
                tasks_with_dependents_to_check.append(supertask)
                tasks_with_supertasks_to_check.append(supertask)

                if supertask not in system:
                    system.add_task(supertask)
                system.add_hierarchy(supertask, task_with_supertasks_to_check)

        # Trim off any tasks that don't have dependee/dependent tasks, nor a
        # superior task with dependee/dependent tasks. These aren't part of the
        # subsystem
        tasks_to_check = collections.deque(system.hierarchy_graph().top_level_tasks())
        visited_tasks = set[UID]()
        while tasks_to_check:
            task_with_dependencies_to_check = tasks_to_check.popleft()

            if task_with_dependencies_to_check in visited_tasks:
                continue
            visited_tasks.add(task_with_dependencies_to_check)

            if not system.dependency_graph().is_isolated(
                task_with_dependencies_to_check
            ):
                continue

            non_downstream_tasks.remove(task_with_dependencies_to_check)

            hierarchies_to_remove = list[tuple[UID, UID]]()
            for subtask in system.hierarchy_graph().subtasks(
                task_with_dependencies_to_check
            ):
                tasks_to_check.append(subtask)
                hierarchies_to_remove.append((task_with_dependencies_to_check, subtask))

            for supertask, subtask in hierarchies_to_remove:
                system.remove_hierarchy(supertask, subtask)
            system.remove_task(task_with_dependencies_to_check)

        # Set basic task attributes
        for task in system:
            attributes = self._attributes_register[task]
            system.set_name(task, attributes.name)
            system.set_description(task, attributes.description)

        # For now, don't try and pass along any of the more complex
        # relational attributes like along progress or importance

        non_downstream_tasks.difference_update(downstream_tasks)

        return system, non_downstream_tasks

    def upstream_subsystem(self, task: UID, /) -> tuple[System, set[UID]]:
        """Return sub-system of all upstream tasks of task.

        Note that the sub-system will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        raise NotImplementedError

        hierarchy_graph = HierarchyGraph()
        dependency_graph = DependencyGraph()

        hierarchy_graph.add_task(task)
        dependency_graph.add_task(task)

        upstream_tasks = set[UID]()
        non_upstream_tasks = set[UID]()

        dependee_tasks_to_check = collections.deque[UID]([task])
        supertasks_to_check = collections.deque[UID]([task])
        subtasks_to_check = collections.deque[UID]()

        visited_dependee_tasks = set[UID]()
        visited_subtasks = set[UID]()
        visited_supertasks = set[UID]()

        while dependee_tasks_to_check or subtasks_to_check or supertasks_to_check:
            while dependee_tasks_to_check:
                task2 = dependee_tasks_to_check.popleft()

                if task2 in visited_dependee_tasks:
                    continue
                visited_dependee_tasks.add(task2)

                for dependee_task in self._dependency_graph.dependee_tasks(task2):
                    upstream_tasks.add(dependee_task)

                    dependee_tasks_to_check.append(dependee_task)
                    subtasks_to_check.append(dependee_task)
                    supertasks_to_check.append(dependee_task)

                    if dependee_task not in hierarchy_graph:
                        hierarchy_graph.add_task(dependee_task)

                    if dependee_task not in dependency_graph:
                        dependency_graph.add_task(dependee_task)
                        dependency_graph.add_dependency(dependee_task, task2)

            while subtasks_to_check:
                task2 = subtasks_to_check.popleft()

                if task2 in visited_subtasks:
                    continue
                visited_subtasks.add(task2)

                for subtask in self._hierarchy_graph.subtasks(task2):
                    upstream_tasks.add(subtask)

                    dependee_tasks_to_check.append(subtask)
                    subtasks_to_check.append(subtask)
                    supertasks_to_check.append(subtask)

                    if subtask not in hierarchy_graph:
                        hierarchy_graph.add_task(subtask)
                        hierarchy_graph.add_hierarchy(task2, subtask)

                    if subtask not in dependency_graph:
                        dependency_graph.add_task(subtask)

            while supertasks_to_check:
                task2 = supertasks_to_check.popleft()

                if task2 in visited_supertasks:
                    continue
                visited_supertasks.add(task2)

                for supertask in self._hierarchy_graph.supertasks(task2):
                    non_upstream_tasks.add(supertask)

                    dependee_tasks_to_check.append(supertask)
                    supertasks_to_check.append(supertask)

                    if supertask not in hierarchy_graph:
                        hierarchy_graph.add_task(supertask)
                        hierarchy_graph.add_hierarchy(supertask, task2)

                    if supertask not in dependency_graph:
                        dependency_graph.add_task(supertask)

        # Trim off any tasks that don't have dependee/dependent tasks, nor a
        # superior task with dependee/dependent tasks. These aren't part of the
        # subsystem
        tasks_to_check = collections.deque(hierarchy_graph.top_level_tasks())
        visited_tasks = set[UID]()
        while tasks_to_check:
            task2 = tasks_to_check.popleft()

            if task2 in visited_tasks:
                continue
            visited_tasks.add(task2)

            if not dependency_graph.is_isolated(task2):
                continue

            non_upstream_tasks.remove(task2)
            tasks_to_check.extend(hierarchy_graph.subtasks(task2))
            hierarchy_graph.remove_task(task2)
            dependency_graph.remove_task(task2)

        # Create a new attributes register with only tasks in the subsystem
        register = AttributesRegister()
        for task in hierarchy_graph:
            attributes = self._attributes_register[task]
            register.add(task)
            register.set_name(task, attributes.name)
            register.set_description(task, attributes.description)

        # Get all the tasks that are in the system, but aren't actually
        # upstream of task
        non_upstream_tasks.difference_update(upstream_tasks)

        return System(register, hierarchy_graph, dependency_graph), non_upstream_tasks

    def connecting_subsystem(
        self, source_task: UID, target_task: UID, /
    ) -> tuple[System, set[UID]]:
        """Return subsystem of tasks between source and target tasks."""
        for task in [source_task, target_task]:
            if task not in self:
                raise TaskDoesNotExistError(task=task)

        source_downstream_subsystem, non_downstream_tasks = self.downstream_subsystem(
            source_task
        )

        try:
            (
                target_upstream_subsystem,
                non_upstream_tasks,
            ) = source_downstream_subsystem.upstream_subsystem(target_task)
        except TaskDoesNotExistError as e:
            raise NoConnectingSubsystemError(
                source_task=source_task, target_task=target_task
            ) from e

        non_connecting_tasks = non_downstream_tasks | non_upstream_tasks
        return target_upstream_subsystem, non_connecting_tasks

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

    def set_name(self, task: UID, name: Name) -> None:
        """Set the name of the specified task."""
        self._attributes_register.set_name(task, name)

    def set_description(self, task: UID, description: Description) -> None:
        """Set the description of the specified task."""
        self._attributes_register.set_description(task, description)

    def _get_dependent_tasks_of_superior_tasks(
        self, task: UID, /
    ) -> Generator[UID, None, None]:
        """Get all the dependent tasks of all the superior tasks of the specified task."""
        visited_dependent_tasks = set[UID]()
        for superior_task in self._hierarchy_graph.superior_tasks_bfs(task):
            for dependent_task in self._dependency_graph.dependent_tasks(superior_task):
                if dependent_task in visited_dependent_tasks:
                    continue
                visited_dependent_tasks.add(dependent_task)
                yield dependent_task

    def _get_dependee_tasks_of_superior_tasks(
        self, task: UID, /
    ) -> Generator[UID, None, None]:
        """Get all the dependee tasks of all the superior tasks of the specified task."""
        visited_dependee_tasks = set[UID]()
        for superior_task in self._hierarchy_graph.superior_tasks_bfs(task):
            for dependee_task in self._dependency_graph.dependee_tasks(superior_task):
                if dependee_task in visited_dependee_tasks:
                    continue
                visited_dependee_tasks.add(dependee_task)
                yield dependee_task

    def set_progress(self, task: UID, progress: Progress) -> None:
        """Set the progress of the specified task."""
        current_progress = self._get_progress_of_concrete_task(task)

        match current_progress:
            case Progress.COMPLETED:
                if progress is not Progress.COMPLETED:
                    if any(
                        self.get_progress(dependent_task) is not Progress.NOT_STARTED
                        for dependent_task in self._dependency_graph.dependent_tasks(
                            task
                        )
                    ):
                        dependent_tasks_with_progress = (
                            (dependent_task, dependent_progress)
                            for dependent_task in self._dependency_graph.dependent_tasks(
                                task
                            )
                            if (dependent_progress := self.get_progress(dependent_task))
                            is not Progress.NOT_STARTED
                        )
                        raise StartedDependentTasksError(
                            task=task,
                            started_dependent_tasks_with_progress=dependent_tasks_with_progress,
                        )

                    if any(
                        self.get_progress(dependent_task) is not Progress.NOT_STARTED
                        for dependent_task in self._get_dependent_tasks_of_superior_tasks(
                            task
                        )
                    ):
                        # TODO: Add subgraph to error
                        raise StartedDependentTasksOfSuperiorTasksError(task=task)
            case Progress.NOT_STARTED:
                if progress is not Progress.NOT_STARTED:
                    if any(
                        self.get_progress(dependee_task) is not Progress.COMPLETED
                        for dependee_task in self._dependency_graph.dependee_tasks(task)
                    ):
                        incomplete_dependee_tasks_with_progress = (
                            (dependee_task, dependee_progress)
                            for dependee_task in self._dependency_graph.dependee_tasks(
                                task
                            )
                            if (dependee_progress := self.get_progress(dependee_task))
                            is not Progress.COMPLETED
                        )
                        raise IncompleteDependeeTasksError(
                            task=task,
                            incomplete_dependee_tasks_with_progress=incomplete_dependee_tasks_with_progress,
                        )

                    if any(
                        self.get_progress(dependee_task) is not Progress.COMPLETED
                        for dependee_task in self._get_dependee_tasks_of_superior_tasks(
                            task
                        )
                    ):
                        # TODO: Add subgraph to error
                        raise IncompleteDependeeTasksOfSuperiorTasksError(task=task)
            case Progress.IN_PROGRESS:
                pass

        self._attributes_register.set_progress(task, progress)

    def set_importance(self, task: UID, importance: Importance | None = None) -> None:
        """Set the importance of the specified task."""
        if importance is None or self._attributes_register[task].importance is not None:
            self._attributes_register.set_importance(task, importance)
            return

        if any(
            self._attributes_register[supertask].importance is not None
            for supertask in self._hierarchy_graph.supertasks(task)
        ):
            supertasks_with_importance = (
                (supertask, supertask_importance)
                for supertask in self._hierarchy_graph.supertasks(task)
                if (
                    supertask_importance := self._attributes_register[
                        supertask
                    ].importance
                )
                is not None
            )
            raise SupertaskHasImportanceError(
                task=task, supertasks_with_importance=supertasks_with_importance
            )

        if any(
            self._attributes_register[superior_task].importance is not None
            for superior_task in self._hierarchy_graph.superior_tasks_bfs(task)
        ):
            # TODO: Get subgraph and importances
            raise SuperiorTaskHasImportanceError(task=task)

        if any(
            self._attributes_register[subtask].importance is not None
            for subtask in self._hierarchy_graph.subtasks(task)
        ):
            subtasks_with_importance = (
                (subtask, subtask_importance)
                for subtask in self._hierarchy_graph.subtasks(task)
                if (subtask_importance := self._attributes_register[subtask].importance)
                is not None
            )
            raise SubtaskHasImportanceError(
                task=task, subtasks_with_importance=subtasks_with_importance
            )

        if any(
            self._attributes_register[inferior_task].importance is not None
            for inferior_task in self._hierarchy_graph.inferior_tasks_bfs(task)
        ):
            # TODO: Get subgraph and importances
            raise InferiorTaskHasImportanceError(task=task)

        self._attributes_register.set_importance(task, importance)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""

        def has_dependency_clash(self: Self, supertask: UID, subtask: UID) -> bool:
            """Quite a complicated little check - read the description.

            Check if any of the dependent-linked-tasks of (the super-task or
            superior-tasks of the super-task) and any dependent-linked-tasks of
            (the sub-task or inferior-tasks of the sub-task) are (superior to or
            inferior to or the same) as one another.
            """
            dependency_linked_tasks_of_superior_tasks_of_supertask = set[UID]()
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

            dependency_linked_tasks_of_inferior_tasks_of_subtask = set[UID]()
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

        self._hierarchy_graph.validate_hierarchy_can_be_added(supertask, subtask)

        if self._dependency_graph.has_path(supertask, subtask):
            connecting_subgraph = self._dependency_graph.connecting_subgraph(
                supertask, subtask
            )
            raise DependencyPathAlreadyExistsFromSuperTaskToSubTaskError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            )
        if self._dependency_graph.has_path(subtask, supertask):
            connecting_subgraph = self._dependency_graph.connecting_subgraph(
                subtask, supertask
            )
            raise DependencyPathAlreadyExistsFromSubTaskToSuperTaskError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
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

        if (
            self._attributes_register[supertask].importance is not None
            or any(
                self._attributes_register[superior_task].importance is not None
                for superior_task in self._hierarchy_graph.superior_tasks_bfs(supertask)
            )
        ) and (
            self._attributes_register[subtask].importance is not None
            or any(
                self._attributes_register[inferior_task].importance is not None
                for inferior_task in self._hierarchy_graph.inferior_tasks_bfs(subtask)
            )
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise MultipleImportancesInHierarchyError

        subtask_progress = self.get_progress(subtask)
        if subtask_progress is not Progress.NOT_STARTED:
            if any(
                self.get_progress(task) is not Progress.COMPLETED
                for task in self._dependency_graph.dependee_tasks(supertask)
            ):
                incomplete_dependee_tasks_of_supertask_with_progress = (
                    (task, progress)
                    for task in self._dependency_graph.dependee_tasks(supertask)
                    if (progress := self.get_progress(task)) is not Progress.COMPLETED
                )
                raise IncompleteDependeeTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    incomplete_dependee_tasks_of_supertask_with_progress=incomplete_dependee_tasks_of_supertask_with_progress,
                )

            if any(
                self.get_progress(task) is not Progress.COMPLETED
                for task in self._get_dependee_tasks_of_superior_tasks(supertask)
            ):
                # TODO: Get proper subgraph
                raise IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    subtask_progress=subtask_progress,
                )

        if subtask is not Progress.COMPLETED:
            if any(
                self.get_progress(task) is not Progress.NOT_STARTED
                for task in self._dependency_graph.dependent_tasks(supertask)
            ):
                started_dependent_tasks_of_supertask_with_progress = (
                    (task, progress)
                    for task in self._dependency_graph.dependent_tasks(supertask)
                    if (progress := self.get_progress(task)) is not Progress.NOT_STARTED
                )
                raise StartedDependentTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    started_dependent_tasks_of_supertask_with_progress=started_dependent_tasks_of_supertask_with_progress,
                )

            if any(
                self.get_progress(task) is not Progress.NOT_STARTED
                for task in self._get_dependent_tasks_of_superior_tasks(supertask)
            ):
                # TODO: Get proper subgraph
                raise StartedDependentTasksOfSuperiorTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    subtask_progress=subtask_progress,
                )

        if self._hierarchy_graph.is_concrete(supertask):
            if (
                supertask_progress := self._get_progress_of_concrete_task(supertask)
            ) is not (subtask_progress := self.get_progress(subtask)):
                raise MismatchedProgressForNewSupertaskError(
                    supertask=supertask,
                    supertask_progress=supertask_progress,
                    subtask=subtask,
                    subtask_progress=subtask_progress,
                )

            self._attributes_register.set_progress(task=supertask, progress=None)

        self._hierarchy_graph.add_hierarchy(supertask, subtask)

    def remove_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Remove the specified hierarchy."""
        if len(self._hierarchy_graph.subtasks(supertask)) == 1:
            subtask_progress = self.get_progress(subtask)
            self._attributes_register.set_progress(supertask, subtask_progress)

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

        self._dependency_graph.validate_dependency_can_be_added(
            dependee_task, dependent_task
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

        if (
            dependee_progress := self.get_progress(dependee_task)
        ) is not Progress.COMPLETED and (
            dependent_progress := self.get_progress(dependent_task)
        ) is not Progress.NOT_STARTED:
            raise DependeeIncompleteDependentStartedError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                dependee_progress=dependee_progress,
                dependent_progress=dependent_progress,
            )

        self._dependency_graph.add_dependency(dependee_task, dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the specified dependency."""
        self._dependency_graph.remove_dependency(dependee_task, dependent_task)

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        return (
            self._get_progress_of_concrete_task(task)
            if self._hierarchy_graph.is_concrete(task)
            else self._get_inferred_progress(task)
        )

    def _get_progress_of_concrete_task(self, task: UID, /) -> Progress:
        """Get the progress of a concrete task."""
        if not self._hierarchy_graph.is_concrete(task):
            raise NotConcreteTaskError(task=task)

        progress = self._attributes_register[task].progress
        assert progress is not None
        return progress

    def _get_inferred_progress(self, task: UID) -> Progress:
        """Return the inferred progress of the specified non-concrete task."""
        if self._hierarchy_graph.is_concrete(task):
            raise ConcreteTaskError(task=task)

        progress: Progress | None = None
        # DFS will get to the concrete tasks faster, so use that
        for inferior_task in self._hierarchy_graph.inferior_tasks_dfs(task):
            if not self._hierarchy_graph.is_concrete(inferior_task):
                continue

            concrete_task_progress = self._get_progress_of_concrete_task(inferior_task)

            match concrete_task_progress:
                case Progress.NOT_STARTED:
                    if progress is Progress.COMPLETED:
                        return Progress.IN_PROGRESS
                    progress = Progress.NOT_STARTED
                case Progress.IN_PROGRESS:
                    return Progress.IN_PROGRESS
                case Progress.COMPLETED:
                    if progress is Progress.NOT_STARTED:
                        return Progress.IN_PROGRESS
                    progress = Progress.COMPLETED

        assert progress is not None
        return progress

    def get_importance(self, task: UID, /) -> Importance | set[Importance] | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance.
        """
        if (importance := self._attributes_register[task].importance) is not None:
            return importance

        return self._get_inferred_importance(task)

    def _get_inferred_importance(self, task: UID, /) -> set[Importance] | None:
        """Return the inferred importance of the specified task with no importance.

        If the task has one or more superior tasks with importances, then
        they'll be returned as part of a set.
        """
        assert self._attributes_register[task].importance is None

        importances = set[Importance]()
        visited = set[UID]()
        queue = collections.deque[UID](self._hierarchy_graph.supertasks(task))
        all_importance_levels = set(Importance)
        # if we've found every possible importance level, no need to keep searching
        while queue and importances != all_importance_levels:
            superior_task = queue.popleft()
            if superior_task in visited:
                continue
            visited.add(superior_task)

            if (
                importance := self._attributes_register[superior_task].importance
            ) is not None:
                importances.add(importance)
                # Don't go any further along this branch, as there'll be no more importances
                continue

            queue.extend(self._hierarchy_graph.supertasks(superior_task))

        return importances or None

    def _is_active(self, task: UID, /) -> bool:
        """Return whether the specified task is active."""
        match self.get_progress(task):
            case Progress.COMPLETED:
                return False
            case Progress.IN_PROGRESS:
                return True
            case Progress.NOT_STARTED:
                return all(
                    self.get_progress(dependee_task) is Progress.COMPLETED
                    for dependee_task in itertools.chain(
                        self._dependency_graph.dependee_tasks(task),
                        self._get_dependee_tasks_of_superior_tasks(task),
                    )
                )

    def _group_by_importance(
        self, tasks: Iterable[UID], /
    ) -> dict[Importance | None, list[UID]]:
        """Return the specified tasks grouped by importance."""
        importance_tasks_map = collections.defaultdict[Importance | None, list[UID]](
            list
        )
        for task in tasks:
            importance = self.get_importance(task)
            if isinstance(importance, set):
                importance = max(importance)
            importance_tasks_map[importance].append(task)

        return importance_tasks_map

    def _get_incomplete_concrete_tasks_in_order_of_ascending_importance(
        self,
    ) -> Generator[set[UID], None, None]:
        """Return the incomplete concrete tasks in order of ascending importance."""
        no_priority_tasks = set[UID]()
        importance_tasks_map = collections.defaultdict[Importance, set[UID]](set)

        for task in self._hierarchy_graph.concrete_tasks():
            if self._get_progress_of_concrete_task(task) is Progress.COMPLETED:
                continue
            importance = self.get_importance(task)
            if importance is None:
                no_priority_tasks.add(task)
                continue
            if isinstance(importance, set):
                importance = max(importance)
            importance_tasks_map[importance].add(task)

        for tasks in itertools.chain(
            [no_priority_tasks],
            (
                importance_tasks_map[importance]
                for importance in sorted(importance_tasks_map.keys())
            ),
        ):
            if not tasks:
                continue
            yield tasks

    def get_active_concrete_tasks_in_order_of_descending_priority(
        self,
    ) -> Generator[tuple[UID, Importance | None], None, None]:
        """Return the active concrete tasks in order of descending priority.

        Tasks are paired with the maximum importance of downstream tasks.
        """

        class PriorityScoreCard:
            """Scorecard for calculating the priority of a task.

            The general gist is that taskA is of higher priority than taskB if
            it is upstream of a higher-importance task, and if it is further progressed.
            """

            def __init__(self, progress: Progress) -> None:
                self.highest_importance: Importance | None = None
                self.progress = progress

            def add_downstream_importance(self, importance: Importance) -> None:
                self.highest_importance = (
                    max(self.highest_importance, importance)
                    if self.highest_importance
                    else importance
                )

            def __eq__(self, other: object) -> bool:
                return (
                    isinstance(other, PriorityScoreCard)
                    and self.highest_importance is other.highest_importance
                    and self.progress is other.progress
                )

            def __lt__(self, other: object) -> bool:
                if not isinstance(other, PriorityScoreCard):
                    raise NotImplementedError

                if not self.highest_importance:
                    return False

                if not other.highest_importance:
                    return True

                if self.highest_importance < other.highest_importance:
                    return False

                return self.progress < other.progress

        concrete_tasks = list(self._hierarchy_graph.concrete_tasks())

        active_concrete_tasks_priority_score_cards_map = {
            task: PriorityScoreCard(self._get_progress_of_concrete_task(task))
            for task in concrete_tasks
            if self._is_active(task)
        }

        incomplete_concrete_tasks = (
            task
            for task in concrete_tasks
            if self._get_progress_of_concrete_task(task) is not Progress.COMPLETED
        )
        incomplete_concrete_tasks_grouped_by_importance = self._group_by_importance(
            incomplete_concrete_tasks
        )
        for (
            importance,
            incomplete_concrete_tasks,
        ) in incomplete_concrete_tasks_grouped_by_importance.items():
            if importance is None:
                continue
            for incomplete_concrete_task in incomplete_concrete_tasks:
                upstream_tasks = set(self._upstream_tasks(incomplete_concrete_task))
                upstream_tasks.add(incomplete_concrete_task)
                for (
                    task,
                    priority_score_card,
                ) in active_concrete_tasks_priority_score_cards_map.items():
                    if task in upstream_tasks:
                        priority_score_card.add_downstream_importance(importance)

        for task, score_card in sorted(
            active_concrete_tasks_priority_score_cards_map.items(),
            key=lambda x: x[1],
            reverse=True,
        ):
            yield (task, score_card.highest_importance)


class SystemView:
    """View of System."""

    def __init__(self, system: ISystemView) -> None:
        """Initialise SystemView."""
        self._system = system

    def __bool__(self) -> bool:
        """Check if system has any tasks."""
        return bool(self._system)

    def __len__(self) -> int:
        """Return number of tasks in system."""
        return len(self._system)

    def __eq__(self, other: object) -> bool:
        """Check if system views are equal."""
        return (
            isinstance(other, SystemView)
            and self.attributes_register() == other.attributes_register()
            and self.hierarchy_graph() == other.hierarchy_graph()
            and self.dependency_graph() == other.dependency_graph()
        )

    def __iter__(self) -> Iterator[UID]:
        """Return an iterator over the tasks in the system."""
        return iter(self._system)

    def __contains__(self, task: UID) -> bool:
        """Check if the specified task exists in the system."""
        return task in self._system

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return self._system.attributes_register()

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._system.hierarchy_graph()

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._system.dependency_graph()

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        return self._system.get_progress(task)

    def get_importance(self, task: UID, /) -> Importance | set[Importance] | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance.
        """
        return self._system.get_importance(task)
