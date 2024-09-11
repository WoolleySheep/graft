"""System and associated classes/exceptions."""

from __future__ import annotations

import collections
import itertools
from typing import TYPE_CHECKING, Any, Protocol

from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
)
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.network_graph import NetworkGraph, NetworkGraphView
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.uid import UID, TasksView

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, MutableMapping

    from graft.domain.tasks.description import Description
    from graft.domain.tasks.name import Name


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
        """Check if the system is not empty."""
        ...

    def tasks(self) -> TasksView:
        """Return a view of the tasks in the system."""
        ...

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        ...

    def network_graph(self) -> NetworkGraphView:
        """Return a view of the network graph."""
        ...

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        ...

    def get_progresses(
        self, tasks: Iterable[UID], /
    ) -> Generator[Progress, None, None]:
        """Yield the progress of each of the specified tasks.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        ...

    def get_importance(self, task: UID, /) -> Importance | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of its
        super-tasks. If it also has no inferred importance, return None.
        """
        ...

    def get_importances(
        self, tasks: Iterable[UID], /
    ) -> Generator[Importance | None, None, None]:
        """Yield the importance of each of the specified tasks.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of a
        task's super-tasks. If it also has no inferred importance, return None.
        """
        ...

    def has_inferred_importance(self, task: UID, /) -> bool:
        """Return whether the specified task has an inferred importance.

        Inferred importance is the highest importance of its supertasks.
        """
        ...


class System:
    """System of task information."""

    @classmethod
    def empty(cls) -> System:
        """Create an empty System."""
        return cls(
            attributes_register=AttributesRegister(),
            network_graph=NetworkGraph.empty(),
        )

    def __init__(
        self,
        attributes_register: AttributesRegister,
        network_graph: NetworkGraph,
    ) -> None:
        """Initialise System."""
        # TODO: Add input validation
        self._attributes_register = attributes_register
        self._network_graph = network_graph

    def __bool__(self) -> bool:
        """Check if the system is not empty."""
        return bool(self._attributes_register)

    def __eq__(self, other: object) -> bool:
        """Check if two systems are equal."""
        return (
            isinstance(other, System)
            and self.attributes_register() == other.attributes_register()
            and self.network_graph() == other.network_graph()
        )

    def tasks(self) -> TasksView:
        """Return a view of the tasks in the system."""
        return self._network_graph.tasks()

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return AttributesRegisterView(self._attributes_register)

    def network_graph(self) -> NetworkGraphView:
        """Return a view of the network graph."""
        return NetworkGraphView(self._network_graph)

    def add_task(self, task: UID, /) -> None:
        """Add a task."""
        self._attributes_register.add(task)
        self._network_graph.add_task(task)

    def remove_task(self, task: UID, /) -> None:
        """Remove a task."""
        self._network_graph.validate_task_can_be_removed(task)

        self._attributes_register.remove(task)
        self._network_graph.remove_task(task)

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
        for superior_task in (
            self._network_graph.hierarchy_graph().superior_tasks(task).tasks()
        ):
            for (
                dependent_task
            ) in self._network_graph.dependency_graph().dependent_tasks(superior_task):
                if dependent_task in visited_dependent_tasks:
                    continue
                visited_dependent_tasks.add(dependent_task)
                yield dependent_task

    def _get_dependee_tasks_of_superior_tasks(
        self, task: UID, /
    ) -> Generator[UID, None, None]:
        """Get all the dependee tasks of all the superior tasks of the specified task."""
        visited_dependee_tasks = set[UID]()
        for superior_task in (
            self._network_graph.hierarchy_graph().superior_tasks(task).tasks()
        ):
            for dependee_task in self._network_graph.dependency_graph().dependee_tasks(
                superior_task
            ):
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
                        dependent_progress is not Progress.NOT_STARTED
                        for dependent_progress in self.get_progresses(
                            self._network_graph.dependency_graph().dependent_tasks(task)
                        )
                    ):
                        dependent_tasks = (
                            self._network_graph.dependency_graph().dependent_tasks(task)
                        )
                        started_dependent_tasks_with_progress = (
                            (dependent_task, dependent_progress)
                            for dependent_task, dependent_progress in zip(
                                dependent_tasks, self.get_progresses(dependent_tasks)
                            )
                            if dependent_progress is not Progress.NOT_STARTED
                        )
                        raise StartedDependentTasksError(
                            task=task,
                            started_dependent_tasks_with_progress=started_dependent_tasks_with_progress,
                        )

                    if any(
                        superior_dependent_progress is not Progress.NOT_STARTED
                        for superior_dependent_progress in self.get_progresses(
                            self._get_dependent_tasks_of_superior_tasks(task)
                        )
                    ):
                        # TODO: Add subgraph to error
                        raise StartedDependentTasksOfSuperiorTasksError(task=task)
            case Progress.NOT_STARTED:
                if progress is not Progress.NOT_STARTED:
                    if any(
                        dependee_progress is not Progress.COMPLETED
                        for dependee_progress in self.get_progresses(
                            self._network_graph.dependency_graph().dependee_tasks(task)
                        )
                    ):
                        dependee_tasks = (
                            self._network_graph.dependency_graph().dependee_tasks(task)
                        )
                        incomplete_dependee_tasks_with_progress = (
                            (dependee_task, dependee_progress)
                            for dependee_task, dependee_progress in zip(
                                dependee_tasks, self.get_progresses(dependee_tasks)
                            )
                            if dependee_progress is not Progress.COMPLETED
                        )
                        raise IncompleteDependeeTasksError(
                            task=task,
                            incomplete_dependee_tasks_with_progress=incomplete_dependee_tasks_with_progress,
                        )

                    if any(
                        superior_dependee_progress is not Progress.COMPLETED
                        for superior_dependee_progress in self.get_progresses(
                            self._get_dependee_tasks_of_superior_tasks(task)
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
            for supertask in self._network_graph.hierarchy_graph().supertasks(task)
        ):
            supertasks_with_importance = (
                (supertask, supertask_importance)
                for supertask in self._network_graph.hierarchy_graph().supertasks(task)
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
            for superior_task in self._network_graph.hierarchy_graph()
            .superior_tasks(task)
            .tasks()
        ):
            # TODO: Get subgraph and importances
            raise SuperiorTaskHasImportanceError(task=task)

        if any(
            self._attributes_register[subtask].importance is not None
            for subtask in self._network_graph.hierarchy_graph().subtasks(task)
        ):
            subtasks_with_importance = (
                (subtask, subtask_importance)
                for subtask in self._network_graph.hierarchy_graph().subtasks(task)
                if (subtask_importance := self._attributes_register[subtask].importance)
                is not None
            )
            raise SubtaskHasImportanceError(
                task=task, subtasks_with_importance=subtasks_with_importance
            )

        if any(
            self._attributes_register[inferior_task].importance is not None
            for inferior_task in self._network_graph.hierarchy_graph()
            .inferior_tasks(task)
            .tasks()
        ):
            # TODO: Get subgraph and importances
            raise InferiorTaskHasImportanceError(task=task)

        self._attributes_register.set_importance(task, importance)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        self._network_graph.validate_hierarchy_can_be_added(supertask, subtask)

        if (
            self._attributes_register[supertask].importance is not None
            or any(
                self._attributes_register[superior_task].importance is not None
                for superior_task in self._network_graph.hierarchy_graph()
                .superior_tasks(supertask)
                .tasks()
            )
        ) and (
            self._attributes_register[subtask].importance is not None
            or any(
                self._attributes_register[inferior_task].importance is not None
                for inferior_task in self._network_graph.hierarchy_graph()
                .inferior_tasks(subtask)
                .tasks()
            )
        ):
            # TODO: Get relevant subgraph and return as part of exception
            raise MultipleImportancesInHierarchyError

        subtask_progress = self.get_progress(subtask)
        if subtask_progress is not Progress.NOT_STARTED:
            if any(
                dependee_progress is not Progress.COMPLETED
                for dependee_progress in self.get_progresses(
                    self._network_graph.dependency_graph().dependee_tasks(supertask)
                )
            ):
                dependee_tasks_of_supertask = (
                    self._network_graph.dependency_graph().dependee_tasks(supertask)
                )
                incomplete_dependee_tasks_of_supertask_with_progress = (
                    (dependee_task, dependee_task_progress)
                    for dependee_task, dependee_task_progress in zip(
                        dependee_tasks_of_supertask,
                        self.get_progresses(dependee_tasks_of_supertask),
                    )
                    if dependee_task_progress is not Progress.COMPLETED
                )
                raise IncompleteDependeeTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    incomplete_dependee_tasks_of_supertask_with_progress=incomplete_dependee_tasks_of_supertask_with_progress,
                )

            if any(
                progress is not Progress.COMPLETED
                for progress in self.get_progresses(
                    self._get_dependee_tasks_of_superior_tasks(supertask)
                )
            ):
                # TODO: Get proper subgraph
                raise IncompleteDependeeTasksOfSuperiorTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    subtask_progress=subtask_progress,
                )

        if subtask is not Progress.COMPLETED:
            if any(
                progress is not Progress.NOT_STARTED
                for progress in self.get_progresses(
                    self._network_graph.dependency_graph().dependent_tasks(supertask)
                )
            ):
                dependent_tasks_of_supertask = (
                    self._network_graph.dependency_graph().dependent_tasks(supertask)
                )
                started_dependent_tasks_of_supertask_with_progress = (
                    (task, progress)
                    for task, progress in zip(
                        dependent_tasks_of_supertask,
                        self.get_progresses(dependent_tasks_of_supertask),
                    )
                    if progress is not Progress.NOT_STARTED
                )
                raise StartedDependentTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    started_dependent_tasks_of_supertask_with_progress=started_dependent_tasks_of_supertask_with_progress,
                )

            if any(
                progress is not Progress.NOT_STARTED
                for progress in self.get_progresses(
                    self._get_dependent_tasks_of_superior_tasks(supertask)
                )
            ):
                # TODO: Get proper subgraph
                raise StartedDependentTasksOfSuperiorTasksOfSupertaskError(
                    supertask=supertask,
                    subtask=subtask,
                    subtask_progress=subtask_progress,
                )

        if self._network_graph.hierarchy_graph().is_concrete(supertask):
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

        self._network_graph.add_hierarchy(supertask, subtask)

    def remove_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Remove the specified hierarchy."""
        if len(self._network_graph.hierarchy_graph().subtasks(supertask)) == 1:
            subtask_progress = self.get_progress(subtask)
            self._attributes_register.set_progress(supertask, subtask_progress)

        self._network_graph.remove_hierarchy(supertask, subtask)

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Add a dependency between the specified tasks."""
        self._network_graph.validate_dependency_can_be_added(
            dependee_task, dependent_task
        )

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

        self._network_graph.add_dependency(dependee_task, dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the specified dependency."""
        self._network_graph.remove_dependency(dependee_task, dependent_task)

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        return next(self.get_progresses([task]))

    def get_progresses(
        self, tasks: Iterable[UID], /
    ) -> Generator[Progress, None, None]:
        """Yield the progress of each of the specified tasks.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """

        def get_progress_recursive(
            task: UID, task_progress_map: MutableMapping[UID, Progress]
        ) -> Progress:
            if self._network_graph.hierarchy_graph().is_concrete(task):
                return self._get_progress_of_concrete_task(task)

            if task in task_progress_map:
                return task_progress_map[task]

            # Get inferred progress
            progress: Progress | None = None
            for subtask in self._network_graph.hierarchy_graph().subtasks(task):
                subtask_progress = get_progress_recursive(subtask, task_progress_map)

                match subtask_progress:
                    case Progress.NOT_STARTED:
                        if progress is Progress.COMPLETED:
                            progress = Progress.IN_PROGRESS
                            break
                        progress = Progress.NOT_STARTED
                    case Progress.IN_PROGRESS:
                        progress = Progress.IN_PROGRESS
                        break
                    case Progress.COMPLETED:
                        if progress is Progress.NOT_STARTED:
                            progress = Progress.IN_PROGRESS
                            break
                        progress = Progress.COMPLETED

            assert progress
            task_progress_map[task] = progress
            return progress

        task_progress_map = dict[UID, Progress]()
        for task in tasks:
            yield get_progress_recursive(task, task_progress_map)

    def _get_progress_of_concrete_task(self, task: UID, /) -> Progress:
        """Get the progress of a concrete task."""
        progress = self._attributes_register[task].progress

        if progress is None:
            raise NotConcreteTaskError(task=task)

        return progress

    def has_inferred_importance(self, task: UID, /) -> bool:
        """Return whether the specified task has an inferred importance.

        Inferred importance is the highest importance of its supertasks.
        """
        return self._attributes_register[task].importance is None and any(
            self._attributes_register[superior_task].importance is not None
            for superior_task in self._network_graph.hierarchy_graph()
            .superior_tasks(task)
            .tasks()
        )

    def get_importance(self, task: UID, /) -> Importance | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of its
        super-tasks. If it also has no inferred importance, return None.
        """
        return next(self.get_importances([task]))

    def get_importances(
        self, tasks: Iterable[UID], /
    ) -> Generator[Importance | None, None, None]:
        """Yield the importance of each of the specified tasks.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of a
        task's super-tasks. If it also has no inferred importance, return None.
        """

        def get_importance_recursive(
            task: UID, task_importance_map: dict[UID, Importance | None]
        ) -> Importance | None:
            if (importance := self._attributes_register[task].importance) is not None:
                return importance

            if task in task_importance_map:
                return task_importance_map[task]

            # Get inferred importance
            highest_importance = None
            for supertask in self._network_graph.hierarchy_graph().supertasks(task):
                supertask_importance = get_importance_recursive(
                    supertask, task_importance_map
                )
                if supertask_importance is None:
                    continue
                if (
                    highest_importance is None
                    or supertask_importance > highest_importance
                ):
                    highest_importance = supertask_importance
                if highest_importance is Importance.HIGH:
                    break

            task_importance_map[task] = highest_importance
            return highest_importance

        task_importance_map = dict[UID, Importance | None]()
        for task in tasks:
            yield get_importance_recursive(task, task_importance_map)

    def _is_active(self, task: UID, /) -> bool:
        """Check whether the specified task is active."""
        match self.get_progress(task):
            case Progress.COMPLETED:
                return False
            case Progress.IN_PROGRESS:
                return True
            case Progress.NOT_STARTED:
                return all(
                    self.get_progress(dependee_task) is Progress.COMPLETED
                    for dependee_task in itertools.chain(
                        self._network_graph.dependency_graph().dependee_tasks(task),
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
            importance_tasks_map[importance].append(task)

        return importance_tasks_map

    def get_active_concrete_tasks_in_order_of_descending_priority(
        self,
    ) -> list[tuple[UID, Importance | None]]:
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

                # TODO: Surely this can be changed into one combined inequality
                if not self.highest_importance:
                    return False

                if not other.highest_importance:
                    return True

                if self.highest_importance < other.highest_importance:
                    return False

                return self.progress < other.progress

        concrete_tasks = list(self._network_graph.hierarchy_graph().concrete_tasks())

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
                upstream_tasks = set(
                    self._network_graph.upstream_tasks(incomplete_concrete_task)
                )
                upstream_tasks.add(incomplete_concrete_task)
                for (
                    task,
                    priority_score_card,
                ) in active_concrete_tasks_priority_score_cards_map.items():
                    if task in upstream_tasks:
                        priority_score_card.add_downstream_importance(importance)

        return [
            (task, score_card.highest_importance)
            for task, score_card in sorted(
                active_concrete_tasks_priority_score_cards_map.items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]


class SystemView:
    """View of System."""

    def __init__(self, system: ISystemView) -> None:
        """Initialise SystemView."""
        self._system = system

    def __bool__(self) -> bool:
        """Check if the system is not empty."""
        return bool(self._system)

    def __eq__(self, other: object) -> bool:
        """Check if system views are equal."""
        return (
            isinstance(other, SystemView)
            and self.attributes_register() == other.attributes_register()
            and self.network_graph() == other.network_graph()
        )

    def tasks(self) -> TasksView:
        """Return a view of the tasks in the system."""
        return self._system.tasks()

    def attributes_register(self) -> AttributesRegisterView:
        """Return a view of the attributes register."""
        return self._system.attributes_register()

    def network_graph(self) -> NetworkGraphView:
        """Return a view of the network graph."""
        return self._system.network_graph()

    def get_progress(self, task: UID, /) -> Progress:
        """Return the progress of the specified task.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        return self._system.get_progress(task)

    def get_progresses(
        self, tasks: Iterable[UID], /
    ) -> Generator[Progress, None, None]:
        """Yield the progress of each of the specified tasks.

        If it is a concrete tasks, returns its progress. If it is a non-concrete
        task, returns its inferred progress.
        """
        return self._system.get_progresses(tasks)

    def get_importance(self, task: UID, /) -> Importance | None:
        """Return the importance of the specified task.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of its
        super-tasks. If it also has no inferred importance, return None.
        """
        return self._system.get_importance(task)

    def get_importances(
        self, tasks: Iterable[UID], /
    ) -> Generator[Importance | None, None, None]:
        """Yield the importance of each of the specified tasks.

        If it has its own importance, return that. If not, return the inferred
        importance. The inferred importance is the highest importance of a
        task's super-tasks. If it also has no inferred importance, return None.
        """
        return self._system.get_importances(tasks)

    def has_inferred_importance(self, task: UID, /) -> bool:
        """Return whether the specified task has an inferred importance.

        Inferred importance is the highest importance of its supertasks.
        """
        return self._system.has_inferred_importance(task)
