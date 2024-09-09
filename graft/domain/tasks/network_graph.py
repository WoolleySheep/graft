from __future__ import annotations

import collections
import itertools
from typing import TYPE_CHECKING, Any, Protocol, Self

from graft.domain.tasks.dependency_graph import DependencyGraph, DependencyGraphView
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import HierarchyGraph, HierarchyGraphView
from graft.domain.tasks.uid import UID, UIDsView

if TYPE_CHECKING:
    from collections.abc import Generator


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


class NoConnectingSubgraphError(Exception):
    """Raised when there is no connecting subsystem between two tasks."""

    def __init__(
        self,
        source_task: UID,
        target_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NoConnectingSubgraphError."""
        self.source_task = source_task
        self.target_task = target_task
        super().__init__(
            f"No connecting subgraph between tasks [{source_task}] and [{target_task}].",
            *args,
            **kwargs,
        )


class INetworkGraphView(Protocol):
    """Interface for a view of a task network graph."""

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        ...

    def __str__(self) -> str:
        """Return a string representation of the graph."""
        ...

    def tasks(self) -> UIDsView:
        """Return a view of the tasks in the graph."""
        ...

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        ...

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        ...

    def downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks downstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        ...

    def upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks upstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        ...

    def has_stream_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a stream path from source to target tasks.

        Same as checking if target task is downstream of source task. If the
        source task and the target task are the same, this function will return
        True.
        """
        ...

    def downstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        ...

    def upstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        ...

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of tasks between source and target tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the source, nor upstream of the target, but are required to connect
        the two. I'm calling these non-connecting tasks.
        """
        ...

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Yield isolated tasks."""
        ...


class NetworkGraph:
    """Graph combining task hierarchies and dependencies."""

    @classmethod
    def empty(cls) -> NetworkGraph:
        """Create an empty NetworkGraph."""
        return cls(DependencyGraph(), HierarchyGraph())

    def __init__(
        self, dependency_graph: DependencyGraph, hierarchy_graph: HierarchyGraph
    ) -> None:
        """Initialise NetworkGraph.

        TODO: Note that this approach does not guarantee that the resultant
        NetworkGraph is valid; some validation will need to be done to ensure
        this.
        """
        self._dependency_graph = dependency_graph
        self._hierarchy_graph = hierarchy_graph

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._dependency_graph)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        return (
            isinstance(other, NetworkGraph)
            and self.dependency_graph() == other.dependency_graph()
            and self.hierarchy_graph() == other.hierarchy_graph()
        )

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        return self._dependency_graph.tasks()

    def dependency_graph(self) -> DependencyGraphView:
        """Return view of dependency graph."""
        return DependencyGraphView(self._dependency_graph)

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return view of hierarchy graph."""
        return HierarchyGraphView(self._hierarchy_graph)

    def add_task(self, task: UID, /) -> None:
        """Add a task to the graph."""
        self._hierarchy_graph.add_task(task)
        self._dependency_graph.add_task(task)

    def validate_task_can_be_removed(self, task: UID, /) -> None:
        """Validate that task can be remoed from the graph."""
        self._dependency_graph.validate_task_can_be_removed(task)
        self._hierarchy_graph.validate_task_can_be_removed(task)

    def remove_task(self, task: UID, /) -> None:
        """Remove a task from the graph."""
        self.validate_task_can_be_removed(task)

        self._hierarchy_graph.remove_task(task)
        self._dependency_graph.remove_task(task)

    def validate_hierarchy_can_be_added(self, supertask: UID, subtask: UID, /) -> None:
        """Validate that hierarchy can be added to the graph."""

        def has_dependency_clash(self: Self, supertask: UID, subtask: UID) -> bool:
            """Quite a complicated little check - read the description.

            Check if any of the dependent-linked-tasks of (the super-task or
            superior-tasks of the super-task) and any dependent-linked-tasks of
            (the sub-task or inferior-tasks of the sub-task) are (superior to or
            inferior to or the same) as one another.
            """
            dependency_linked_tasks_of_superior_tasks_of_supertask = set[UID]()
            for superior_task in itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks(supertask).tasks()
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
                [subtask], self._hierarchy_graph.inferior_tasks(subtask).tasks()
            ):
                dependency_linked_tasks_of_inferior_tasks_of_subtask.update(
                    self._dependency_graph.dependee_tasks(inferior_task)
                )
                dependency_linked_tasks_of_inferior_tasks_of_subtask.update(
                    self._dependency_graph.dependent_tasks(inferior_task)
                )

            return any(
                task
                in superior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask.tasks()
                or task
                in inferior_tasks_of_dependency_linked_tasks_of_superior_tasks_of_supertask.tasks()
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

        if self.has_stream_path(supertask, subtask):
            # TODO: Get relevant subgraph and return as part of exception
            raise StreamPathFromSuperTaskToSubTaskExistsError(supertask, subtask)

        if self.has_stream_path(subtask, supertask):
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

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Create a new hierarchy between the specified tasks."""
        self.validate_hierarchy_can_be_added(supertask, subtask)
        self._hierarchy_graph.add_hierarchy(supertask, subtask)

    def remove_hierarchy(self, supertask: UID, subtask: UID) -> None:
        """Remove the specified hierarchy."""
        self._hierarchy_graph.remove_hierarchy(supertask, subtask)

    def validate_dependency_can_be_added(
        self, dependee_task: UID, dependent_task: UID, /
    ) -> None:
        """Validate that dependency can be added to the graph."""

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
                self._hierarchy_graph.superior_tasks(dependee_task).tasks(),
                self._hierarchy_graph.inferior_tasks(dependee_task).tasks(),
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
                self._hierarchy_graph.superior_tasks(dependent_task).tasks(),
                self._hierarchy_graph.inferior_tasks(dependent_task).tasks(),
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

        if self.has_stream_path(dependent_task, dependee_task):
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

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Add a dependency between the specified tasks."""
        self.validate_dependency_can_be_added(dependee_task, dependent_task)
        self._dependency_graph.add_dependency(dependee_task, dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the specified dependency."""
        self._dependency_graph.remove_dependency(dependee_task, dependent_task)

    def downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
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

    def upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
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

    def has_stream_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a stream path from source to target tasks.

        Same as checking if target task is downstream of source task. If the
        source task and the target task are the same, this function will return
        True.
        """
        for task in [source_task, target_task]:
            if task not in self.tasks():
                raise TaskDoesNotExistError(task)

        return source_task == target_task or target_task in self.downstream_tasks(
            source_task
        )

    def _has_stream_path_from_source_to_inferior_task_of_target(
        self, source_task: UID, target_task: UID
    ) -> bool:
        """Check if there is a stream path from source-task to an inferior task of target-task."""
        inferior_tasks_of_target = set(
            self._hierarchy_graph.inferior_tasks(target_task).tasks()
        )
        return any(
            downstream_task in inferior_tasks_of_target
            for downstream_task in self.downstream_tasks(source_task)
        )

    def _has_stream_path_from_inferior_task_of_source_to_target(
        self, source_task: UID, target_task: UID
    ) -> bool:
        """Check if there is a stream path from an inferior task of source-task to target-task."""
        inferior_tasks_of_source = set(
            self._hierarchy_graph.inferior_tasks(source_task).tasks()
        )
        return any(
            upstream_task in inferior_tasks_of_source
            for upstream_task in self.upstream_tasks(target_task)
        )

    def downstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        subgraph = NetworkGraph.empty()
        subgraph.add_task(task)

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

                    if dependent_task not in subgraph.tasks():
                        subgraph.add_task(dependent_task)
                    subgraph.add_dependency(
                        task_with_dependents_to_check, dependent_task
                    )

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

                if task not in subgraph.tasks():
                    subgraph.add_task(subtask)
                subgraph.add_hierarchy(task_with_subtasks_to_check, subtask)

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

                if supertask not in subgraph.tasks():
                    subgraph.add_task(supertask)
                subgraph.add_hierarchy(supertask, task_with_supertasks_to_check)

        # Trim off any tasks that don't have dependee/dependent tasks, nor a
        # superior task with dependee/dependent tasks. These aren't part of the
        # subsystem
        tasks_to_check = collections.deque(subgraph.hierarchy_graph().top_level_tasks())
        visited_tasks = set[UID]()
        while tasks_to_check:
            task_with_dependencies_to_check = tasks_to_check.popleft()

            if task_with_dependencies_to_check in visited_tasks:
                continue
            visited_tasks.add(task_with_dependencies_to_check)

            if not subgraph.dependency_graph().is_isolated(
                task_with_dependencies_to_check
            ):
                continue

            non_downstream_tasks.remove(task_with_dependencies_to_check)

            hierarchies_to_remove = list[tuple[UID, UID]]()
            for subtask in subgraph.hierarchy_graph().subtasks(
                task_with_dependencies_to_check
            ):
                tasks_to_check.append(subtask)
                hierarchies_to_remove.append((task_with_dependencies_to_check, subtask))

            for supertask, subtask in hierarchies_to_remove:
                subgraph.remove_hierarchy(supertask, subtask)
            subgraph.remove_task(task_with_dependencies_to_check)

        non_downstream_tasks.difference_update(downstream_tasks)

        return subgraph, non_downstream_tasks

    def upstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        raise NotImplementedError

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of tasks between source and target tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the source, nor upstream of the target, but are required to connect
        the two. I'm calling these non-connecting tasks.
        """
        for task in [source_task, target_task]:
            if task not in self.tasks():
                raise TaskDoesNotExistError(task=task)

        source_downstream_subgraph, non_downstream_tasks = self.downstream_subgraph(
            source_task
        )

        try:
            (
                target_upstream_subgraph,
                non_upstream_tasks,
            ) = source_downstream_subgraph.upstream_subgraph(target_task)
        except TaskDoesNotExistError as e:
            raise NoConnectingSubgraphError(
                source_task=source_task, target_task=target_task
            ) from e

        non_connecting_tasks = non_downstream_tasks | non_upstream_tasks
        return target_upstream_subgraph, non_connecting_tasks

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        return self._dependency_graph.is_isolated(
            task
        ) and self._hierarchy_graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        for task in self.tasks():
            if self.is_isolated(task):
                yield task


class NetworkGraphView:
    """View of Network Graph."""

    def __init__(self, graph: INetworkGraphView) -> None:
        """Initialise NetworkGraphView."""
        self._graph = graph

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._graph)

    def __eq__(self, other: object) -> bool:
        """Check if graph views are equal."""
        return (
            isinstance(other, NetworkGraphView)
            and self.hierarchy_graph() == other.hierarchy_graph()
            and self.dependency_graph() == other.dependency_graph()
        )

    def tasks(self) -> UIDsView:
        """Return a view of the tasks in the graph."""
        return self._graph.tasks()

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._graph.hierarchy_graph()

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._graph.dependency_graph()

    def downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks downstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self._graph.downstream_tasks(task)

    def upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks upstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self._graph.upstream_tasks(task)

    def has_stream_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a stream path from source to target tasks.

        Same as checking if target task is downstream of source task. If the
        source task and the target task are the same, this function will return
        True.
        """
        return self._graph.has_stream_path(source_task, target_task)

    def downstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        return self._graph.downstream_subgraph(task)

    def upstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        return self._graph.upstream_subgraph(task)
