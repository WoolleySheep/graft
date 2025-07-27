"""System and associated classes/exceptions."""

from __future__ import annotations

import copy
import itertools
from typing import TYPE_CHECKING, Any, Protocol

from graft.domain.tasks.attributes_register import (
    AttributesRegister,
    AttributesRegisterView,
    AttributesSubregisterBuilder,
)
from graft.domain.tasks.importance import Importance
from graft.domain.tasks.network_graph import (
    NetworkGraph,
    NetworkGraphView,
    NetworkSubgraphBuilder,
)
from graft.domain.tasks.progress import Progress
from graft.domain.tasks.uid import UID
from graft.utils import unique

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable, MutableMapping

    from graft.domain.tasks.description import Description
    from graft.domain.tasks.name import Name
    from graft.domain.tasks.uid import TasksView


class MultipleImportancesInHierarchyError(Exception):
    """Raised when there are multiple importances in a hierarchy."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise MultipleImportanceInHierarchyError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subsystem = subsystem
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


class DownstreamTasksHaveStartedError(Exception):
    """Raised when a task has downstream tasks that have started.

    Task cannot be uncompleted, as dependent tasks depend on it being completed.
    """

    def __init__(
        self,
        task: UID,
        started_downstream_tasks: Iterable[tuple[UID, Progress]],
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.task = task
        self.started_downstream_tasks_to_progress_map = dict(started_downstream_tasks)
        self.subsystem = subsystem
        super().__init__(
            f"Task [{task}] has started dependent tasks of superior tasks.",
            *args,
            **kwargs,
        )


class UpstreamTasksAreIncompleteError(Exception):
    """Raised when a task has upstream tasks that are incomplete.

    Task cannot be started, as dependee tasks must be completed before the task can be started.
    """

    def __init__(
        self,
        task: UID,
        incomplete_upstream_tasks: Iterable[tuple[UID, Progress]],
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.task = task
        self.incomplete_upstream_tasks_to_progress_map = dict(incomplete_upstream_tasks)
        self.subsystem = subsystem
        super().__init__(
            f"Task [{task}] has incomplete dependee tasks of superior tasks.",
            *args,
            **kwargs,
        )


class UpstreamTasksOfSupertaskAreIncompleteError(Exception):
    """Raised when tasks upstream of the supertask have not already completed.

    Started subtask cannot be connected, as upstream tasks must be completed
    before the task can be started.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subtask_progress: Progress,
        incomplete_upstream_tasks: Iterable[tuple[UID, Progress]],
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NotCompletedDependeeTasksOfSuperiorTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subtask_progress = subtask_progress
        self.upstream_task_incomplete_map = dict(incomplete_upstream_tasks)
        self.subsystem = subsystem
        super().__init__(
            f"Supertask [{supertask}] has incomplete dependee tasks of superior tasks.",
            *args,
            **kwargs,
        )


class DownstreamTasksOfSupertaskHaveStartedError(Exception):
    """Raised when tasks downstream of the supertask have already started.

    Incomplete subtask cannot be connected, as downstream tasks depend on it being completed.
    """

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subtask_progress: Progress,
        started_downstream_tasks: Iterable[tuple[UID, Progress]],
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise StartedDependentTasksOfSuperiorTasksOfSupertaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subtask_progress = subtask_progress
        self.downstream_task_started_map = dict(started_downstream_tasks)
        self.subsystem = subsystem
        super().__init__(
            f"Supertask [{supertask}] has started dependent tasks of superior tasks.",
            *args,
            **kwargs,
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


class SuperiorTasksHaveImportanceError(Exception):
    """Raised when a superior task has an importance."""

    def __init__(
        self,
        task: UID,
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise SuperiorTaskHasImportanceError."""
        self.task = task
        self.subsystem = subsystem
        super().__init__(
            f"Task [{task}] has superior tasks with importance", *args, **kwargs
        )


class InferiorTasksHaveImportanceError(Exception):
    """Raised when a inferior task has an importance."""

    def __init__(
        self,
        task: UID,
        subsystem: System,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise InferiorTaskHasImportanceError."""
        self.task = task
        self.subsystem = subsystem
        super().__init__(
            f"Task [{task}] has inferior tasks with importance", *args, **kwargs
        )


class ISystemView(Protocol):
    """Interface for a view of a task system."""

    def __bool__(self) -> bool:
        """Check if the system is not empty."""
        ...

    def clone(self) -> System:
        """Return a clone of the system."""
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


class SubsystemBuilder:
    """Builder for a subsystem of a system."""

    def __init__(self, system: ISystemView) -> None:
        self._system = system
        self._network_graph_builder = NetworkSubgraphBuilder(
            self._system.network_graph()
        )
        self._attributes_register_builder = AttributesSubregisterBuilder(
            self._system.attributes_register()
        )

    def add_task(self, task: UID, /) -> None:
        self._network_graph_builder.add_task(task)
        self._attributes_register_builder.add_task(task)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        self._network_graph_builder.add_hierarchy(supertask, subtask)
        self._attributes_register_builder.add_task(supertask)
        self._attributes_register_builder.add_task(subtask)

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        self._network_graph_builder.add_dependency(dependee_task, dependent_task)
        self._attributes_register_builder.add_task(dependee_task)
        self._attributes_register_builder.add_task(dependent_task)

    def add_superior_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_superior_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_inferior_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_inferior_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_hierarchy_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        added_tasks = self._network_graph_builder.add_hierarchy_connecting_subgraph(
            source_tasks, target_tasks
        )
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_hierarchy_component_subgraph(self, task: UID) -> set[UID]:
        added_tasks = self._network_graph_builder.add_hierarchy_component_subgraph(task)
        for task_ in added_tasks:
            self._attributes_register_builder.add_task(task_)
        return added_tasks

    def add_proceeding_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_proceeding_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_following_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_following_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_dependency_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        added_tasks = self._network_graph_builder.add_dependency_connecting_subgraph(
            source_tasks, target_tasks
        )
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_dependency_component_subgraph(self, task: UID) -> set[UID]:
        added_tasks = self._network_graph_builder.add_dependency_component_subgraph(
            task
        )
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_upstream_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_upstream_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_downstream_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_downstream_subgraph(tasks)
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        added_tasks = self._network_graph_builder.add_connecting_subgraph(
            source_tasks, target_tasks
        )
        for task in added_tasks:
            self._attributes_register_builder.add_task(task)
        return added_tasks

    def add_component_subgraph(self, task: UID, /) -> set[UID]:
        added_tasks = self._network_graph_builder.add_component_subgraph(task)
        for task_ in added_tasks:
            self._attributes_register_builder.add_task(task_)
        return added_tasks

    def build(self) -> System:
        network_subgraph = self._network_graph_builder.build()
        attributes_register = self._attributes_register_builder.build()

        for concrete_task, progress in zip(
            network_subgraph.hierarchy_graph().concrete_tasks(),
            self._system.get_progresses(
                network_subgraph.hierarchy_graph().concrete_tasks()
            ),
            strict=True,
        ):
            attributes_register.set_progress(concrete_task, progress)

        for top_level_task, importance in zip(
            network_subgraph.hierarchy_graph().top_level_tasks(),
            self._system.get_importances(
                network_subgraph.hierarchy_graph().top_level_tasks()
            ),
            strict=True,
        ):
            attributes_register.set_importance(top_level_task, importance)

        return System(
            attributes_register=attributes_register, network_graph=network_subgraph
        )


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
        if not isinstance(other, System):
            return NotImplemented

        return (
            self.attributes_register() == other.attributes_register()
            and self.network_graph() == other.network_graph()
        )

    def clone(self) -> System:
        """Return a clone of the system."""
        return copy.deepcopy(self)

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

    def set_progress(self, task: UID, progress: Progress) -> None:
        """Set the progress of the specified task."""
        current_progress = self._get_progress_of_concrete_task(task)

        match current_progress:
            case Progress.COMPLETED:
                if progress is not Progress.COMPLETED and any(
                    downstream_task_progress is not Progress.NOT_STARTED
                    for downstream_task_progress in self.get_progresses(
                        unique(
                            itertools.chain.from_iterable(
                                map(
                                    self._network_graph.dependency_graph().dependent_tasks,
                                    itertools.chain(
                                        [task],
                                        self._network_graph.hierarchy_graph().superior_tasks(
                                            [task]
                                        ),
                                    ),
                                )
                            )
                        )
                    )
                ):
                    task_and_its_superior_tasks = [
                        task,
                        *self._network_graph.hierarchy_graph().superior_tasks([task]),
                    ]
                    tasks_one_step_downstream_of_task = list(
                        unique(
                            itertools.chain.from_iterable(
                                map(
                                    self._network_graph.dependency_graph().dependent_tasks,
                                    task_and_its_superior_tasks,
                                )
                            )
                        )
                    )
                    started_tasks_downstream_of_task_and_their_progresses = {
                        task: progress
                        for task, progress in zip(
                            tasks_one_step_downstream_of_task,
                            self.get_progresses(tasks_one_step_downstream_of_task),
                            strict=True,
                        )
                        if progress is not Progress.NOT_STARTED
                    }

                    intersecting_task_and_superior_tasks_to_started_dependent_tasks_map = {
                        task: self._network_graph.dependency_graph().dependent_tasks(
                            task
                        )
                        & started_tasks_downstream_of_task_and_their_progresses.keys()
                        for task in task_and_its_superior_tasks
                        if not self._network_graph.dependency_graph()
                        .dependent_tasks(task)
                        .isdisjoint(
                            started_tasks_downstream_of_task_and_their_progresses.keys()
                        )
                    }

                    builder = SubsystemBuilder(self)
                    builder.add_hierarchy_connecting_subgraph(
                        intersecting_task_and_superior_tasks_to_started_dependent_tasks_map.keys(),
                        [task],
                    )
                    for (
                        intersecting_task,
                        started_downstream_tasks,
                    ) in intersecting_task_and_superior_tasks_to_started_dependent_tasks_map.items():
                        for started_downstream_task in started_downstream_tasks:
                            builder.add_dependency(
                                intersecting_task, started_downstream_task
                            )

                    raise DownstreamTasksHaveStartedError(
                        task=task,
                        started_downstream_tasks=started_tasks_downstream_of_task_and_their_progresses.items(),
                        subsystem=builder.build(),
                    )
            case Progress.NOT_STARTED:
                if progress is not Progress.NOT_STARTED and any(
                    upstream_task_progress is not Progress.COMPLETED
                    for upstream_task_progress in self.get_progresses(
                        unique(
                            itertools.chain.from_iterable(
                                map(
                                    self._network_graph.dependency_graph().dependee_tasks,
                                    itertools.chain(
                                        [task],
                                        self._network_graph.hierarchy_graph().superior_tasks(
                                            [task]
                                        ),
                                    ),
                                )
                            )
                        )
                    )
                ):
                    task_and_its_superior_tasks = [
                        task,
                        *self._network_graph.hierarchy_graph().superior_tasks([task]),
                    ]
                    tasks_one_step_upstream_of_task = list(
                        unique(
                            itertools.chain.from_iterable(
                                map(
                                    self._network_graph.dependency_graph().dependee_tasks,
                                    task_and_its_superior_tasks,
                                )
                            )
                        )
                    )
                    incomplete_tasks_upstream_of_task_and_their_progresses = {
                        task: progress
                        for task, progress in zip(
                            tasks_one_step_upstream_of_task,
                            self.get_progresses(tasks_one_step_upstream_of_task),
                            strict=True,
                        )
                        if progress is not Progress.COMPLETED
                    }

                    intersecting_task_and_superior_tasks_to_incomplete_dependee_tasks_map = {
                        task: self._network_graph.dependency_graph().dependee_tasks(
                            task
                        )
                        & incomplete_tasks_upstream_of_task_and_their_progresses.keys()
                        for task in task_and_its_superior_tasks
                        if not self._network_graph.dependency_graph()
                        .dependee_tasks(task)
                        .isdisjoint(
                            incomplete_tasks_upstream_of_task_and_their_progresses.keys()
                        )
                    }

                    builder = SubsystemBuilder(self)
                    builder.add_hierarchy_connecting_subgraph(
                        intersecting_task_and_superior_tasks_to_incomplete_dependee_tasks_map.keys(),
                        [task],
                    )
                    for (
                        intersecting_task,
                        incomplete_upstream_tasks,
                    ) in intersecting_task_and_superior_tasks_to_incomplete_dependee_tasks_map.items():
                        for incomplete_upstream_task in incomplete_upstream_tasks:
                            builder.add_dependency(
                                incomplete_upstream_task, intersecting_task
                            )
                    raise UpstreamTasksAreIncompleteError(
                        task=task,
                        incomplete_upstream_tasks=incomplete_tasks_upstream_of_task_and_their_progresses.items(),
                        subsystem=builder.build(),
                    )
            case Progress.IN_PROGRESS:
                pass

        self._attributes_register.set_progress(task, progress)

    def set_importance(self, task: UID, importance: Importance | None = None) -> None:
        """Set the importance of the specified task."""
        if importance is None or self._attributes_register[task].importance is not None:
            self._attributes_register.set_importance(task, importance)
            return

        if any(
            self._attributes_register[superior_task].importance is not None
            for superior_task in self._network_graph.hierarchy_graph().superior_tasks(
                [task]
            )
        ):
            superior_tasks = self._network_graph.hierarchy_graph().superior_tasks(
                [task],
                stop_condition=lambda task_: self._attributes_register[task_].importance
                is not None,
            )
            superior_tasks_with_importance = filter(
                lambda task_: self._attributes_register[task_].importance is not None,
                superior_tasks,
            )
            builder = SubsystemBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                superior_tasks_with_importance, [task]
            )

            raise SuperiorTasksHaveImportanceError(task=task, subsystem=builder.build())

        if any(
            self._attributes_register[inferior_task].importance is not None
            for inferior_task in self._network_graph.hierarchy_graph().inferior_tasks(
                [task]
            )
        ):
            inferior_tasks = self._network_graph.hierarchy_graph().inferior_tasks(
                [task],
                stop_condition=lambda task_: self._attributes_register[task_].importance
                is not None,
            )
            inferior_tasks_with_importance = filter(
                lambda task_: self._attributes_register[task_].importance is not None,
                inferior_tasks,
            )
            builder = SubsystemBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                [task], inferior_tasks_with_importance
            )
            raise InferiorTasksHaveImportanceError(task=task, subsystem=builder.build())

        self._attributes_register.set_importance(task, importance)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        self._network_graph.validate_hierarchy_can_be_added(supertask, subtask)

        if any(
            self._attributes_register[task].importance is not None
            for task in itertools.chain(
                [supertask],
                self._network_graph.hierarchy_graph().superior_tasks([supertask]),
            )
        ) and any(
            self._attributes_register[task].importance is not None
            for task in itertools.chain(
                [subtask],
                self._network_graph.hierarchy_graph().inferior_tasks([subtask]),
            )
        ):
            supertask_and_its_superior_tasks_with_importances = filter(
                lambda task: self._attributes_register[task].importance is not None,
                itertools.chain(
                    [supertask],
                    self._network_graph.hierarchy_graph().superior_tasks([supertask]),
                ),
            )

            subtask_and_its_inferior_tasks_with_importances = filter(
                lambda task: self._attributes_register[task].importance is not None,
                itertools.chain(
                    [subtask],
                    self._network_graph.hierarchy_graph().inferior_tasks([subtask]),
                ),
            )

            builder = SubsystemBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                supertask_and_its_superior_tasks_with_importances,
                [supertask],
            )
            builder.add_hierarchy_connecting_subgraph(
                [subtask], subtask_and_its_inferior_tasks_with_importances
            )

            raise MultipleImportancesInHierarchyError(
                supertask=supertask, subtask=subtask, subsystem=builder.build()
            )

        subtask_progress = self.get_progress(subtask)
        if subtask_progress is not Progress.NOT_STARTED and any(
            progress is not Progress.COMPLETED
            for progress in self.get_progresses(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._network_graph.dependency_graph().dependee_tasks,
                            itertools.chain(
                                [supertask],
                                self._network_graph.hierarchy_graph().superior_tasks(
                                    [supertask]
                                ),
                            ),
                        )
                    )
                )
            )
        ):
            supertask_and_its_superior_tasks = list(
                itertools.chain(
                    [supertask],
                    self._network_graph.hierarchy_graph().superior_tasks([supertask]),
                )
            )

            dependee_tasks_of_supertask_and_its_superior_tasks = list(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._network_graph.dependency_graph().dependee_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            dependee_tasks_of_supertask_and_its_superior_tasks_with_progresses = (
                (task, progress)
                for task, progress in zip(
                    dependee_tasks_of_supertask_and_its_superior_tasks,
                    self.get_progresses(
                        dependee_tasks_of_supertask_and_its_superior_tasks
                    ),
                    strict=True,
                )
            )

            incomplete_dependee_tasks_of_supertask_and_its_superior_tasks_to_progress_map = dict(
                filter(
                    lambda task_with_progress: task_with_progress[1]
                    is not Progress.COMPLETED,
                    dependee_tasks_of_supertask_and_its_superior_tasks_with_progresses,
                )
            )

            supertask_and_its_superior_tasks_to_incomplete_dependee_tasks_map = {
                task: incomplete_dependee_tasks
                for task in supertask_and_its_superior_tasks
                if (
                    incomplete_dependee_tasks := (
                        self._network_graph.dependency_graph().dependee_tasks(task)
                        & incomplete_dependee_tasks_of_supertask_and_its_superior_tasks_to_progress_map.keys()
                    )
                )
            }

            builder = SubsystemBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                supertask_and_its_superior_tasks_to_incomplete_dependee_tasks_map.keys(),
                [supertask],
            )
            for (
                supertask_or_its_superior_task,
                incomplete_dependee_tasks_of_supertask_or_its_superior_task,
            ) in supertask_and_its_superior_tasks_to_incomplete_dependee_tasks_map.items():
                for (
                    incomplete_dependee_task_of_supertask_or_its_superior_task
                ) in incomplete_dependee_tasks_of_supertask_or_its_superior_task:
                    builder.add_dependency(
                        incomplete_dependee_task_of_supertask_or_its_superior_task,
                        supertask_or_its_superior_task,
                    )
            builder.add_task(subtask)

            raise UpstreamTasksOfSupertaskAreIncompleteError(
                supertask=supertask,
                subtask=subtask,
                subtask_progress=subtask_progress,
                incomplete_upstream_tasks=incomplete_dependee_tasks_of_supertask_and_its_superior_tasks_to_progress_map.items(),
                subsystem=builder.build(),
            )

        if subtask_progress is not Progress.COMPLETED and any(
            progress is not Progress.NOT_STARTED
            for progress in self.get_progresses(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._network_graph.dependency_graph().dependent_tasks,
                            itertools.chain(
                                [supertask],
                                self._network_graph.hierarchy_graph().superior_tasks(
                                    [supertask]
                                ),
                            ),
                        )
                    )
                )
            )
        ):
            supertask_and_its_superior_tasks = list(
                itertools.chain(
                    [supertask],
                    self._network_graph.hierarchy_graph().superior_tasks([supertask]),
                )
            )

            dependent_tasks_of_supertask_and_its_superior_tasks = list(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._network_graph.dependency_graph().dependent_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            dependent_tasks_of_supertask_and_its_superior_tasks_with_progresses = (
                (task, progress)
                for task, progress in zip(
                    dependent_tasks_of_supertask_and_its_superior_tasks,
                    self.get_progresses(
                        dependent_tasks_of_supertask_and_its_superior_tasks
                    ),
                    strict=True,
                )
            )

            started_dependent_tasks_of_supertask_and_its_superior_tasks_to_progress_map = dict(
                filter(
                    lambda task_with_progress: task_with_progress[1]
                    is not Progress.NOT_STARTED,
                    dependent_tasks_of_supertask_and_its_superior_tasks_with_progresses,
                )
            )

            supertask_and_its_superior_tasks_to_started_dependent_tasks_map = {
                task: started_dependent_tasks
                for task in supertask_and_its_superior_tasks
                if (
                    started_dependent_tasks := (
                        self._network_graph.dependency_graph().dependent_tasks(task)
                        & started_dependent_tasks_of_supertask_and_its_superior_tasks_to_progress_map.keys()
                    )
                )
            }

            builder = SubsystemBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                supertask_and_its_superior_tasks_to_started_dependent_tasks_map.keys(),
                [supertask],
            )
            for (
                supertask_or_its_superior_task,
                started_dependent_tasks_of_supertask_or_its_superior_task,
            ) in (
                supertask_and_its_superior_tasks_to_started_dependent_tasks_map.items()
            ):
                for (
                    started_dependent_task_of_supertask_or_its_superior_task
                ) in started_dependent_tasks_of_supertask_or_its_superior_task:
                    builder.add_dependency(
                        supertask_or_its_superior_task,
                        started_dependent_task_of_supertask_or_its_superior_task,
                    )
            builder.add_task(subtask)

            raise DownstreamTasksOfSupertaskHaveStartedError(
                supertask=supertask,
                subtask=subtask,
                subtask_progress=subtask_progress,
                started_downstream_tasks=started_dependent_tasks_of_supertask_and_its_superior_tasks_to_progress_map.items(),
                subsystem=builder.build(),
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

        More efficient that getting the progresses one-by-one as determining progress
        for non-concrete tasks requires graph traversal.
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
            for superior_task in self._network_graph.hierarchy_graph().superior_tasks(
                [task]
            )
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

    def clone(self) -> System:
        """Return a clone of the system."""
        return self._system.clone()

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
