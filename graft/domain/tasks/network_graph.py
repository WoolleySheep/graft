from __future__ import annotations

import collections
import itertools
from typing import TYPE_CHECKING, Any, Protocol, Self

from graft.domain.tasks.dependency_graph import (
    DependencyGraph,
    DependencyGraphView,
    IDependencyGraphView,
)
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HierarchyGraph,
    HierarchyGraphView,
    IHierarchyGraphView,
)
from graft.domain.tasks.uid import UID, TasksView

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable


def _unique[T](iterable: Iterable[T]) -> Generator[T, None, None]:
    """Yield unique items from an iterable."""
    seen = set[T]()
    for item in iterable:
        if item in seen:
            continue
        seen.add(item)
        yield item


def _does_iterable_contain_values[T](
    iterable: Iterable[T],
) -> tuple[bool, Iterable[T]]:
    """Check if an iterable contains values.

    Returns an un-iterated copy of the iterable so the iterable can be used as if this
    function was never called.
    """
    iterable1, iterable2 = itertools.tee(iterable)
    try:
        next(iterable1)
    except StopIteration:
        return False, iterable2
    return True, iterable2


class DependencyIntroducesNetworkCycleError(Exception):
    """Raised when adding the dependency introduces a cycle to the network graph."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency from dependee-task [{dependee_task}] to dependent-task [{dependent_task}] introduces cycle into network graph",
            *args,
            **kwargs,
        )


class HierarchyIntroducesNetworkCycleError(Exception):
    """Raised when adding the hierarchy introduces a cycle to the network graph."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy from supertask [{supertask}] to subtask [{subtask}] introduces cycle into network graph",
            *args,
            **kwargs,
        )


class HierarchyIntroducesDependencyDuplicationError(Exception):
    """Raised when a hierarchy would introduce a dependency duplication."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy from supertask [{supertask}] to subtask [{subtask}] would duplicate a dependency.",
            *args,
            **kwargs,
        )


class HierarchyIntroducesDependencyCrossoverError(Exception):
    """Raised when a hierarchy would introduce a dependency crossover."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy from supertask [{supertask}] to subtask [{subtask}] would crossover a dependency.",
            *args,
            **kwargs,
        )


class DependencyIntroducesDependencyDuplicationError(Exception):
    """Raised when a dependency would introduce a dependency duplication."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency from dependee_task [{dependee_task}] to dependent_task [{dependent_task}] would duplicate a dependency.",
            *args,
            **kwargs,
        )


class DependencyIntroducesDependencyCrossoverError(Exception):
    """Raised when a dependency would introduce a dependency crossover."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency from dependee_task [{dependee_task}] to dependent_task [{dependent_task}] would crossover a dependency.",
            *args,
            **kwargs,
        )


class DependencyBetweenHierarchyLevelsError(Exception):
    """Raised when there a dependency is added between levels of a hierarchy."""

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


class NoConnectingMultiSubgraphError(Exception):
    """Raised when there is no connecting subsystem between two tasks."""

    def __init__(
        self,
        source_tasks: set[UID],
        target_tasks: set[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NoConnectingSubgraphError."""
        self.source_tasks = source_tasks
        self.target_tasks = target_tasks
        super().__init__(
            f"No connecting subgraph between tasks {source_tasks} and {target_tasks}.",
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

    def tasks(self) -> TasksView:
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
        """Create an empty network graph."""
        return cls(DependencyGraph(), HierarchyGraph())

    @classmethod
    def clone(cls, graph: INetworkGraphView) -> NetworkGraph:
        """Create a clone of a network graph from an interface."""
        hierarchy_graph = HierarchyGraph.clone(graph.hierarchy_graph())
        dependency_graph = DependencyGraph.clone(graph.dependency_graph())
        return cls(dependency_graph, hierarchy_graph)

    def __init__(
        self, dependency_graph: DependencyGraph, hierarchy_graph: HierarchyGraph
    ) -> None:
        """Initialise NetworkGraph."""
        # TODO: Note that this approach does not guarantee that the resultant
        # NetworkGraph is valid; more validation will need to be done to ensure
        # this. Could hack around this by instantiating an empty network, then adding
        # every dependency and every hierarchy from the two respective arguments one at
        # a time. But the real holy grail is to validate everything all at once.
        if dependency_graph.tasks() != hierarchy_graph.tasks():
            msg = "Tasks in dependency graph and hierarchy graph must be the same."
            raise ValueError(msg)

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

    def tasks(self) -> TasksView:
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
        """Validate that task can be removed from the graph."""
        self._dependency_graph.validate_task_can_be_removed(task)
        self._hierarchy_graph.validate_task_can_be_removed(task)

    def remove_task(self, task: UID, /) -> None:
        """Remove a task from the graph."""
        self.validate_task_can_be_removed(task)

        self._hierarchy_graph.remove_task(task)
        self._dependency_graph.remove_task(task)

    def validate_hierarchy_can_be_added(self, supertask: UID, subtask: UID, /) -> None:
        """Validate that hierarchy can be added to the graph."""

        def has_dependency_duplication_with_upstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are duplicate dependencies with an upstream hierarchy.

            Aka: Check if any of the tasks one step upstream of the supertask are
            superior-or-equal to any dependent-tasks of (the sub-task or inferior-tasks
            of the sub-task).
            """
            tasks_a_single_step_upstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks(supertask).tasks()
            ):
                tasks_a_single_step_upstream_of_the_supertask.update(
                    self._dependency_graph.dependee_tasks(
                        supertask_or_its_superior_task
                    )
                )

            if not tasks_a_single_step_upstream_of_the_supertask:
                return False

            tasks_a_single_step_upstream_of_the_supertask_and_their_inferior_tasks = {
                *tasks_a_single_step_upstream_of_the_supertask,
                *self._hierarchy_graph.inferior_tasks_multi(
                    tasks_a_single_step_upstream_of_the_supertask
                ).tasks(),
            }
            for subtask_or_its_inferior_task in itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks(subtask).tasks()
            ):
                for dependee_task in self._dependency_graph.dependee_tasks(
                    subtask_or_its_inferior_task
                ):
                    if (
                        dependee_task
                        in tasks_a_single_step_upstream_of_the_supertask_and_their_inferior_tasks
                    ):
                        return True

            return False

        def has_dependency_duplication_with_downstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are duplicate dependencies with a downstream hierarchy.

             Aka: Check if any of the tasks one step downstream of the supertask
            are superior-or-equal to any of the dependee-tasks of the (sub-task or
            inferior-tasks of the sub-task).
            """
            tasks_a_single_step_downstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks(supertask).tasks()
            ):
                tasks_a_single_step_downstream_of_the_supertask.update(
                    self._dependency_graph.dependent_tasks(
                        supertask_or_its_superior_task
                    )
                )

            if not tasks_a_single_step_downstream_of_the_supertask:
                return False

            tasks_a_single_step_downstream_of_the_supertask_and_their_inferior_tasks = {
                *tasks_a_single_step_downstream_of_the_supertask,
                *self._hierarchy_graph.inferior_tasks_multi(
                    tasks_a_single_step_downstream_of_the_supertask
                ).tasks(),
            }
            for subtask_or_its_inferior_task in itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks(subtask).tasks()
            ):
                for dependent_task in self._dependency_graph.dependent_tasks(
                    subtask_or_its_inferior_task
                ):
                    if (
                        dependent_task
                        in tasks_a_single_step_downstream_of_the_supertask_and_their_inferior_tasks
                    ):
                        return True

            return False

        def has_dependency_crossover_with_upstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are any dependency crossovers with an upstream hierarchy.

            Check if any of the tasks one step upstream of the super-task are inferior
            to any of the dependee-tasks of the (sub-task or inferior-tasks of the
            sub-task).
            """
            supertask_and_its_superior_tasks = itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks(supertask).tasks()
            )
            tasks_a_single_step_upstream_of_the_supertask = _unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            (
                has_tasks_upstream_of_the_supertask,
                tasks_a_single_step_upstream_of_the_supertask,
            ) = _does_iterable_contain_values(
                tasks_a_single_step_upstream_of_the_supertask
            )
            if not has_tasks_upstream_of_the_supertask:
                return False

            superior_tasks_of_tasks_a_single_step_upstream_of_the_supertask = (
                self._hierarchy_graph.superior_tasks_multi(
                    tasks_a_single_step_upstream_of_the_supertask
                ).tasks()
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks(subtask).tasks()
            )

            dependee_tasks_of_subtask_and_its_inferior_tasks = _unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            return any(
                superior_tasks_of_tasks_a_single_step_upstream_of_the_supertask.contains(
                    dependee_tasks_of_subtask_and_its_inferior_tasks
                )
            )

        def has_dependency_crossover_with_downstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are any dependency crossovers with a downstream hierarchy.

            Check if any of the tasks one step downstream of the super-task are inferior
            to any of the dependent-tasks of the (sub-task or inferior-tasks of the
            sub-task).
            """
            supertask_and_its_superior_tasks = itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks(supertask).tasks()
            )
            tasks_a_single_step_downstream_of_the_supertask = _unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            (
                has_tasks_downstream_of_the_supertask,
                tasks_a_single_step_downstream_of_the_supertask,
            ) = _does_iterable_contain_values(
                tasks_a_single_step_downstream_of_the_supertask
            )
            if not has_tasks_downstream_of_the_supertask:
                return False

            superior_tasks_of_tasks_a_single_step_downstream_of_the_supertask = (
                self._hierarchy_graph.superior_tasks_multi(
                    tasks_a_single_step_downstream_of_the_supertask
                ).tasks()
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks(subtask).tasks()
            )

            dependent_tasks_of_subtask_and_its_inferior_tasks = _unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            return any(
                superior_tasks_of_tasks_a_single_step_downstream_of_the_supertask.contains(
                    dependent_tasks_of_subtask_and_its_inferior_tasks
                )
            )

        self._hierarchy_graph.validate_hierarchy_can_be_added(supertask, subtask)

        # Check if there is a stream path from the supertask to the subtask or any of the subtask's inferiors
        subtask_and_its_inferior_tasks = set(
            itertools.chain(
                [subtask], self.hierarchy_graph().inferior_tasks(subtask).tasks()
            )
        )
        if any(
            task in subtask_and_its_inferior_tasks
            for task in self.downstream_tasks(supertask)
        ):
            supertask_downstream_subgraph, _ = self.downstream_subgraph(supertask)
            subtask_inferior_tasks_subgraph = (
                self.hierarchy_graph().inferior_tasks(subtask).subgraph()
            )
            intersecting_tasks = (
                supertask_downstream_subgraph.tasks()
                & subtask_inferior_tasks_subgraph.tasks()
            )
            subtask_connecting_hierarchy_subgraph = (
                subtask_inferior_tasks_subgraph.superior_tasks_multi(
                    intersecting_tasks
                ).subgraph()
            )
            connecting_subgraph, _ = (
                supertask_downstream_subgraph.upstream_subgraph_multi(
                    intersecting_tasks
                )
            )

            connecting_subgraph.update_hierarchy(subtask_connecting_hierarchy_subgraph)

            raise HierarchyIntroducesNetworkCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            )

        # Check if there is a stream path from the subtask or any subtasks's inferiors to the supertask
        subtask_and_its_inferior_tasks = set(
            itertools.chain(
                [subtask], self.hierarchy_graph().inferior_tasks(subtask).tasks()
            )
        )
        if any(
            task in subtask_and_its_inferior_tasks
            for task in self.upstream_tasks(supertask)
        ):
            # TODO: Have NetworkGraph.upstream_subgraph return a view of
            # the network graph, same as HierarchyGraph.inferior_tasks
            # returns a view of a hierarchy graph
            supertask_upstream_subgraph, _ = self.upstream_subgraph(supertask)
            subtask_inferior_tasks_subgraph = (
                self.hierarchy_graph().inferior_tasks(subtask).subgraph()
            )
            intersecting_tasks = (
                supertask_upstream_subgraph.tasks()
                & subtask_inferior_tasks_subgraph.tasks()
            )
            subtask_connecting_hierarchy_subgraph = (
                subtask_inferior_tasks_subgraph.superior_tasks_multi(
                    intersecting_tasks
                ).subgraph()
            )
            connecting_subgraph, _ = (
                supertask_upstream_subgraph.downstream_subgraph_multi(
                    intersecting_tasks
                )
            )

            connecting_subgraph.update_hierarchy(subtask_connecting_hierarchy_subgraph)

            raise HierarchyIntroducesNetworkCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            )

        if has_dependency_duplication_with_upstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_superior_subgraph = self._hierarchy_graph.superior_tasks(
                supertask
            ).subgraph()
            tasks_a_single_step_upstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in supertask_superior_subgraph.tasks():
                tasks_a_single_step_upstream_of_the_supertask.update(
                    self._dependency_graph.dependee_tasks(
                        supertask_or_its_superior_task
                    )
                )

            subtask_inferior_subgraph = self._hierarchy_graph.inferior_tasks(
                subtask
            ).subgraph()
            dependee_tasks_of_either_subtask_or_inferior_task_of_subtask = set[UID]()
            for subtask_or_its_inferior_task in subtask_inferior_subgraph.tasks():
                dependee_tasks_of_either_subtask_or_inferior_task_of_subtask.update(
                    self._dependency_graph.dependee_tasks(subtask_or_its_inferior_task)
                )

            inferior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask = (
                self._hierarchy_graph.inferior_tasks_multi(
                    tasks_a_single_step_upstream_of_the_supertask,
                    stop_condition=lambda task: task
                    in dependee_tasks_of_either_subtask_or_inferior_task_of_subtask,
                ).subgraph()
            )
            intersecting_tasks_in_upstream_hierarchy_subgraph = (
                inferior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask.tasks()
                & dependee_tasks_of_either_subtask_or_inferior_task_of_subtask
            )
            upstream_hierarchy_subgraph = inferior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask.superior_tasks_multi(
                intersecting_tasks_in_upstream_hierarchy_subgraph
            ).subgraph()

            dependencies_that_link_hierarchy_subgraphs = list[tuple[UID, UID]]()
            connecting_top_level_tasks = set[UID]()
            for top_level_task in upstream_hierarchy_subgraph.top_level_tasks():
                for dependent_task in self._dependency_graph.dependent_tasks(
                    top_level_task
                ):
                    if dependent_task not in supertask_superior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (top_level_task, dependent_task)
                    )
                    connecting_top_level_tasks.add(dependent_task)

            trimmed_supertask_superior_subgraph = (
                supertask_superior_subgraph.inferior_tasks_multi(
                    connecting_top_level_tasks
                ).subgraph()
            )

            connecting_concrete_tasks = set[UID]()
            for concrete_task in upstream_hierarchy_subgraph.concrete_tasks():
                for dependent_task in self._dependency_graph.dependent_tasks(
                    concrete_task
                ):
                    if dependent_task not in subtask_inferior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (concrete_task, dependent_task)
                    )
                    connecting_concrete_tasks.add(dependent_task)

            trimmed_subtask_inferior_subgraph = (
                subtask_inferior_subgraph.superior_tasks_multi(
                    connecting_concrete_tasks
                ).subgraph()
            )

            complete_subgraph = NetworkGraph.empty()
            complete_subgraph.update_hierarchy(trimmed_supertask_superior_subgraph)
            complete_subgraph.update_hierarchy(trimmed_subtask_inferior_subgraph)
            complete_subgraph.update_hierarchy(upstream_hierarchy_subgraph)
            for (
                dependee_task,
                dependent_task,
            ) in dependencies_that_link_hierarchy_subgraphs:
                complete_subgraph.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyDuplicationError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=complete_subgraph,
            )

        if has_dependency_duplication_with_downstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_superior_subgraph = self._hierarchy_graph.superior_tasks(
                supertask
            ).subgraph()
            tasks_a_single_step_downstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in supertask_superior_subgraph.tasks():
                tasks_a_single_step_downstream_of_the_supertask.update(
                    self._dependency_graph.dependent_tasks(
                        supertask_or_its_superior_task
                    )
                )

            subtask_inferior_subgraph = self._hierarchy_graph.inferior_tasks(
                subtask
            ).subgraph()
            dependent_tasks_of_either_subtask_or_inferior_task_of_subtask = set[UID]()
            for subtask_or_its_inferior_task in subtask_inferior_subgraph.tasks():
                dependent_tasks_of_either_subtask_or_inferior_task_of_subtask.update(
                    self._dependency_graph.dependent_tasks(subtask_or_its_inferior_task)
                )

            inferior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask = (
                self._hierarchy_graph.inferior_tasks_multi(
                    tasks_a_single_step_downstream_of_the_supertask,
                    stop_condition=lambda task: task
                    in dependent_tasks_of_either_subtask_or_inferior_task_of_subtask,
                ).subgraph()
            )
            intersecting_tasks_in_downstream_hierarchy_subgraph = (
                inferior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask.tasks()
                & dependent_tasks_of_either_subtask_or_inferior_task_of_subtask
            )
            downstream_hierarchy_subgraph = inferior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask.superior_tasks_multi(
                intersecting_tasks_in_downstream_hierarchy_subgraph
            ).subgraph()

            dependencies_that_link_hierarchy_subgraphs = list[tuple[UID, UID]]()
            connecting_top_level_tasks = set[UID]()
            for top_level_task in downstream_hierarchy_subgraph.top_level_tasks():
                for dependee_task in self._dependency_graph.dependee_tasks(
                    top_level_task
                ):
                    if dependee_task not in supertask_superior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (dependee_task, top_level_task)
                    )
                    connecting_top_level_tasks.add(dependee_task)

            trimmed_supertask_superior_subgraph = (
                supertask_superior_subgraph.inferior_tasks_multi(
                    connecting_top_level_tasks
                ).subgraph()
            )

            connecting_concrete_tasks = set[UID]()
            for concrete_task in downstream_hierarchy_subgraph.concrete_tasks():
                for dependee_task in self._dependency_graph.dependee_tasks(
                    concrete_task
                ):
                    if dependee_task not in subtask_inferior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (dependee_task, concrete_task)
                    )
                    connecting_concrete_tasks.add(dependee_task)

            trimmed_subtask_inferior_subgraph = (
                subtask_inferior_subgraph.superior_tasks_multi(
                    connecting_concrete_tasks
                ).subgraph()
            )

            complete_subgraph = NetworkGraph.empty()
            complete_subgraph.update_hierarchy(trimmed_supertask_superior_subgraph)
            complete_subgraph.update_hierarchy(trimmed_subtask_inferior_subgraph)
            complete_subgraph.update_hierarchy(downstream_hierarchy_subgraph)
            for (
                dependee_task,
                dependent_task,
            ) in dependencies_that_link_hierarchy_subgraphs:
                complete_subgraph.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyDuplicationError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=complete_subgraph,
            )

        if has_dependency_crossover_with_upstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_superior_subgraph = self._hierarchy_graph.superior_tasks(
                supertask
            ).subgraph()
            tasks_a_single_step_upstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in supertask_superior_subgraph.tasks():
                tasks_a_single_step_upstream_of_the_supertask.update(
                    self._dependency_graph.dependee_tasks(
                        supertask_or_its_superior_task
                    )
                )

            subtask_inferior_subgraph = self._hierarchy_graph.inferior_tasks(
                subtask
            ).subgraph()
            dependee_tasks_of_either_subtask_or_inferior_task_of_subtask = set[UID]()
            for subtask_or_its_inferior_task in subtask_inferior_subgraph.tasks():
                dependee_tasks_of_either_subtask_or_inferior_task_of_subtask.update(
                    self._dependency_graph.dependee_tasks(subtask_or_its_inferior_task)
                )

            superior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask = (
                self._hierarchy_graph.superior_tasks_multi(
                    tasks_a_single_step_upstream_of_the_supertask,
                    stop_condition=lambda task: task
                    in dependee_tasks_of_either_subtask_or_inferior_task_of_subtask,
                ).subgraph()
            )
            intersecting_tasks_in_upstream_hierarchy_subgraph = (
                superior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask.tasks()
                & dependee_tasks_of_either_subtask_or_inferior_task_of_subtask
            )
            upstream_hierarchy_subgraph = superior_subgraph_of_tasks_a_single_step_upstream_of_the_supertask.inferior_tasks_multi(
                intersecting_tasks_in_upstream_hierarchy_subgraph
            ).subgraph()

            dependencies_that_link_hierarchy_subgraphs = list[tuple[UID, UID]]()

            connecting_top_level_tasks = set[UID]()
            for concrete_task in upstream_hierarchy_subgraph.concrete_tasks():
                for dependent_task in self._dependency_graph.dependent_tasks(
                    concrete_task
                ):
                    if dependent_task not in supertask_superior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (concrete_task, dependent_task)
                    )
                    connecting_top_level_tasks.add(dependent_task)

            trimmed_supertask_superior_subgraph = (
                supertask_superior_subgraph.inferior_tasks_multi(
                    connecting_top_level_tasks
                ).subgraph()
            )

            connecting_concrete_tasks = set[UID]()
            for top_level_task in upstream_hierarchy_subgraph.top_level_tasks():
                for dependent_task in self._dependency_graph.dependent_tasks(
                    top_level_task
                ):
                    if dependent_task not in subtask_inferior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (top_level_task, dependent_task)
                    )
                    connecting_concrete_tasks.add(dependent_task)

            trimmed_subtask_inferior_subgraph = (
                subtask_inferior_subgraph.superior_tasks_multi(
                    connecting_concrete_tasks
                ).subgraph()
            )

            complete_subgraph = NetworkGraph.empty()
            complete_subgraph.update_hierarchy(trimmed_supertask_superior_subgraph)
            complete_subgraph.update_hierarchy(trimmed_subtask_inferior_subgraph)
            complete_subgraph.update_hierarchy(upstream_hierarchy_subgraph)
            for (
                dependee_task,
                dependent_task,
            ) in dependencies_that_link_hierarchy_subgraphs:
                complete_subgraph.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyCrossoverError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=complete_subgraph,
            )

        if has_dependency_crossover_with_downstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_superior_subgraph = self._hierarchy_graph.superior_tasks(
                supertask
            ).subgraph()
            tasks_a_single_step_downstream_of_the_supertask = set[UID]()
            for supertask_or_its_superior_task in supertask_superior_subgraph.tasks():
                tasks_a_single_step_downstream_of_the_supertask.update(
                    self._dependency_graph.dependent_tasks(
                        supertask_or_its_superior_task
                    )
                )

            subtask_inferior_subgraph = self._hierarchy_graph.inferior_tasks(
                subtask
            ).subgraph()
            dependent_tasks_of_either_subtask_or_inferior_task_of_subtask = set[UID]()
            for subtask_or_its_inferior_task in subtask_inferior_subgraph.tasks():
                dependent_tasks_of_either_subtask_or_inferior_task_of_subtask.update(
                    self._dependency_graph.dependent_tasks(subtask_or_its_inferior_task)
                )

            superior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask = (
                self._hierarchy_graph.superior_tasks_multi(
                    tasks_a_single_step_downstream_of_the_supertask,
                    stop_condition=lambda task: task
                    in dependent_tasks_of_either_subtask_or_inferior_task_of_subtask,
                ).subgraph()
            )
            intersecting_tasks_in_downstream_hierarchy_subgraph = (
                superior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask.tasks()
                & dependent_tasks_of_either_subtask_or_inferior_task_of_subtask
            )
            downstream_hierarchy_subgraph = superior_subgraph_of_tasks_a_single_step_downstream_of_the_supertask.inferior_tasks_multi(
                intersecting_tasks_in_downstream_hierarchy_subgraph
            ).subgraph()

            dependencies_that_link_hierarchy_subgraphs = list[tuple[UID, UID]]()

            connecting_top_level_tasks = set[UID]()
            for concrete_task in downstream_hierarchy_subgraph.concrete_tasks():
                for dependee_task in self._dependency_graph.dependee_tasks(
                    concrete_task
                ):
                    if dependee_task not in supertask_superior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (dependee_task, concrete_task)
                    )
                    connecting_top_level_tasks.add(dependee_task)

            trimmed_supertask_superior_subgraph = (
                supertask_superior_subgraph.inferior_tasks_multi(
                    connecting_top_level_tasks
                ).subgraph()
            )

            connecting_concrete_tasks = set[UID]()
            for top_level_task in downstream_hierarchy_subgraph.top_level_tasks():
                for dependee_task in self._dependency_graph.dependee_tasks(
                    top_level_task
                ):
                    if dependee_task not in subtask_inferior_subgraph.tasks():
                        continue
                    dependencies_that_link_hierarchy_subgraphs.append(
                        (dependee_task, top_level_task)
                    )
                    connecting_concrete_tasks.add(dependee_task)

            trimmed_subtask_inferior_subgraph = (
                subtask_inferior_subgraph.superior_tasks_multi(
                    connecting_concrete_tasks
                ).subgraph()
            )

            complete_subgraph = NetworkGraph.empty()
            complete_subgraph.update_hierarchy(trimmed_supertask_superior_subgraph)
            complete_subgraph.update_hierarchy(trimmed_subtask_inferior_subgraph)
            complete_subgraph.update_hierarchy(downstream_hierarchy_subgraph)
            for (
                dependee_task,
                dependent_task,
            ) in dependencies_that_link_hierarchy_subgraphs:
                complete_subgraph.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyCrossoverError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=complete_subgraph,
            )

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
            raise DependencyBetweenHierarchyLevelsError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            )

        if self._hierarchy_graph.has_path(dependent_task, dependee_task):
            connecting_subgraph = self._hierarchy_graph.connecting_subgraph(
                dependent_task, dependee_task
            )
            raise DependencyBetweenHierarchyLevelsError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            )

        if self._has_stream_path_from_source_or_inferior_task_of_source_to_target_or_inferior_task_of_target(
            dependent_task, dependee_task
        ):
            # TODO: Create the subgraph and raise a DependencyIntroducesNetworkCycleError
            pass

        # TODO: Check for DependencyIntroducesNetworkCycleError
        #   - Dependee-task or subtask of dependee-task is downstream of dependent-task or subtask of dependent-task
        #   - And others (do upstream checks)
        # TODO: Check for DependencyIntroducesDependencyDuplicationError
        # TODO: Check for DependencyIntroducesDependencyCrossoverError

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

    # TODO: Replace update, update_hierarchy and update_dependency with a builder class
    # to keep these helper functions away from the proper code
    def update(self, graph: INetworkGraphView) -> None:
        """Update the graph with the specified graph.

        Use this method with EXTREME CAUTION; the order in which tasks,
        hierarchies and dependencies are added cannot be controlled, so I
        recommend only using it as a helper method when you know it won't fail.
        """
        for task in graph.tasks():
            if task in self.tasks():
                continue
            self.add_task(task)

        for supertask, subtask in graph.hierarchy_graph().hierarchies():
            if (supertask, subtask) in self.hierarchy_graph().hierarchies():
                continue
            self.add_hierarchy(supertask, subtask)

        for dependee_task, dependent_task in graph.dependency_graph().dependencies():
            if (
                dependee_task,
                dependent_task,
            ) in self.dependency_graph().dependencies():
                continue
            self.add_dependency(dependee_task, dependent_task)

    def update_hierarchy(self, graph: IHierarchyGraphView) -> None:
        """Update the graph with the specified hierarchy graph.

        Use this method with EXTREME CAUTION; the order in which tasks and
        hierarchies are added cannot be controlled, so I recommend only
        using it as a helper method when you know it won't fail.
        """
        for task in graph.tasks():
            if task in self.tasks():
                continue
            self.add_task(task)

        for supertask, subtask in graph.hierarchies():
            if (supertask, subtask) in self.hierarchy_graph().hierarchies():
                continue
            self.add_hierarchy(supertask, subtask)

    def update_dependency(self, graph: IDependencyGraphView) -> None:
        """Update the graph with the specified dependency graph.

        Use this method with EXTREME CAUTION; the order in which tasks and
        dependencies are added cannot be controlled, so I recommend only
        using it as a helper method when you know it won't fail.
        """
        for task in graph.tasks():
            if task in self.tasks():
                continue
            self.add_task(task)

        for dependee_task, dependent_task in graph.dependencies():
            if (
                dependee_task,
                dependent_task,
            ) in self.dependency_graph().dependencies():
                continue
            self.add_dependency(dependee_task, dependent_task)

    def downstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks downstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self.downstream_tasks_multi([task])

    def upstream_tasks(self, task: UID, /) -> Generator[UID, None, None]:
        """Return tasks upstream of task.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self.upstream_tasks_multi([task])

    def downstream_tasks_multi(
        self, tasks: Iterable[UID]
    ) -> Generator[UID, None, None]:
        """Return tasks downstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        # TODO: Could potentially get clever here and only evaluate the necessary tasks,
        # as yielding downstream tasks allows for a potential early exit.
        # Would need to create some sort of container for a pop-left deque that only
        # evaluates its starting iterable as needed
        starting_tasks = list(tasks)

        downstream_tasks_to_check = collections.deque(
            _unique(
                itertools.chain.from_iterable(
                    map(self._dependency_graph.dependent_tasks, starting_tasks)
                )
            )
        )
        supertasks_to_check = collections.deque(
            _unique(
                itertools.chain.from_iterable(
                    map(self._hierarchy_graph.supertasks, starting_tasks)
                )
            )
        )

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

    def upstream_tasks_multi(
        self, tasks: Iterable[UID], /
    ) -> Generator[UID, None, None]:
        """Return tasks upstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        starting_tasks = list(tasks)

        upstream_tasks_to_check = collections.deque(
            _unique(
                itertools.chain.from_iterable(
                    map(self._dependency_graph.dependee_tasks, starting_tasks)
                )
            )
        )
        supertasks_to_check = collections.deque(
            _unique(
                itertools.chain.from_iterable(
                    map(self._hierarchy_graph.supertasks, starting_tasks)
                )
            )
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

    def _has_stream_path_from_source_or_inferior_task_of_source_to_target_or_inferior_task_of_target(
        self, source_task: UID, target_task: UID
    ) -> bool:
        """Check if there is a stream path from source-task or an inferior task of source-task to target-task or an inferior task of target-task."""
        source_task_and_inferior_tasks_of_source = {
            source_task,
            *self._hierarchy_graph.inferior_tasks(source_task).tasks(),
        }

        target_task_and_inferior_tasks_of_target = itertools.chain(
            [target_task],
            self._hierarchy_graph.inferior_tasks(target_task).tasks(),
        )

        (
            target_task_and_inferior_tasks_of_target1,
            target_task_and_inferior_tasks_of_target2,
        ) = itertools.tee(target_task_and_inferior_tasks_of_target)

        return any(
            task in source_task_and_inferior_tasks_of_source
            for task in itertools.chain(
                target_task_and_inferior_tasks_of_target1,
                self.upstream_tasks_multi(target_task_and_inferior_tasks_of_target2),
            )
        )

    def downstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks correctly.
        I'm calling these non-downstream tasks and are returned along with the
        subgraph.
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

                for subtask in self._hierarchy_graph.subtasks(
                    task_with_subtasks_to_check
                ):
                    downstream_tasks.add(subtask)
                    tasks_with_dependents_to_check.append(subtask)
                    tasks_with_subtasks_to_check.append(subtask)
                    tasks_with_supertasks_to_check.append(subtask)

                    if subtask not in subgraph.tasks():
                        subgraph.add_task(subtask)
                    if (
                        task_with_subtasks_to_check,
                        subtask,
                    ) not in subgraph.hierarchy_graph().hierarchies():
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
                    if (
                        supertask,
                        task_with_supertasks_to_check,
                    ) not in subgraph.hierarchy_graph().hierarchies():
                        subgraph.add_hierarchy(supertask, task_with_supertasks_to_check)

        non_downstream_tasks.difference_update(downstream_tasks)

        # Trim off any tasks that don't have dependee/dependent tasks, nor a
        # superior task with dependee/dependent tasks. These aren't part of the
        # subsystem
        tasks_to_check = collections.deque(subgraph.hierarchy_graph().top_level_tasks())
        visited_tasks = set[UID]()
        while tasks_to_check:
            task_with_dependencies_to_check = tasks_to_check.popleft()

            if task_with_dependencies_to_check not in non_downstream_tasks:
                continue

            if task_with_dependencies_to_check in visited_tasks:
                continue
            visited_tasks.add(task_with_dependencies_to_check)

            if not subgraph.dependency_graph().is_isolated(
                task_with_dependencies_to_check
            ):
                continue

            # Get a concrete copy of the subtasks, as you'll be removing
            # hierarchies and don't want to modify what you're iterating over
            for subtask in list(
                subgraph.hierarchy_graph().subtasks(task_with_dependencies_to_check)
            ):
                subgraph.remove_hierarchy(task_with_dependencies_to_check, subtask)
                if subgraph.hierarchy_graph().is_top_level(subtask):
                    tasks_to_check.append(subtask)
            subgraph.remove_task(task_with_dependencies_to_check)

            non_downstream_tasks.remove(task_with_dependencies_to_check)

        return subgraph, non_downstream_tasks

    def downstream_subgraph_multi(
        self, tasks: Iterable[UID], /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all tasks downstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of any of the tasks, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks and are returned along
        with the subgraph.
        """
        # TODO: Make this more efficient - currently horrible
        combined_subgraph = NetworkGraph.empty()
        combined_non_downstream_tasks = set[UID]()
        for task in tasks:
            subgraph, non_downstream_tasks = self.downstream_subgraph(task)
            combined_subgraph.update(subgraph)

            combined_non_downstream_tasks.difference_update(subgraph.tasks())
            combined_non_downstream_tasks.update(non_downstream_tasks)

        return combined_subgraph, combined_non_downstream_tasks

    def upstream_subgraph(self, task: UID, /) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        subgraph = NetworkGraph.empty()
        subgraph.add_task(task)

        upstream_tasks = set[UID]([task])
        non_upstream_tasks = set[UID]()

        tasks_with_dependees_to_check = collections.deque[UID]([task])
        tasks_with_supertasks_to_check = collections.deque[UID]([task])
        tasks_with_subtasks_to_check = collections.deque[UID]()

        tasks_with_checked_dependees = set[UID]()
        tasks_with_checked_subtasks = set[UID]()
        tasks_with_checked_supertasks = set[UID]()

        while (
            tasks_with_dependees_to_check
            or tasks_with_subtasks_to_check
            or tasks_with_supertasks_to_check
        ):
            while tasks_with_dependees_to_check:
                task_with_dependees_to_check = tasks_with_dependees_to_check.popleft()

                if task_with_dependees_to_check in tasks_with_checked_dependees:
                    continue
                tasks_with_checked_dependees.add(task_with_dependees_to_check)

                for dependee_task in self._dependency_graph.dependee_tasks(
                    task_with_dependees_to_check
                ):
                    upstream_tasks.add(dependee_task)
                    tasks_with_dependees_to_check.append(dependee_task)
                    tasks_with_subtasks_to_check.append(dependee_task)
                    tasks_with_supertasks_to_check.append(dependee_task)

                    if dependee_task not in subgraph.tasks():
                        subgraph.add_task(dependee_task)
                    subgraph.add_dependency(dependee_task, task_with_dependees_to_check)

            while tasks_with_subtasks_to_check:
                task_with_subtasks_to_check = tasks_with_subtasks_to_check.popleft()

                if task_with_subtasks_to_check in tasks_with_checked_subtasks:
                    continue
                tasks_with_checked_subtasks.add(task_with_subtasks_to_check)

                for subtask in self._hierarchy_graph.subtasks(
                    task_with_subtasks_to_check
                ):
                    upstream_tasks.add(subtask)
                    tasks_with_dependees_to_check.append(subtask)
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
                    non_upstream_tasks.add(supertask)
                    tasks_with_dependees_to_check.append(supertask)
                    tasks_with_supertasks_to_check.append(supertask)

                    if supertask not in subgraph.tasks():
                        subgraph.add_task(supertask)
                    subgraph.add_hierarchy(supertask, task_with_supertasks_to_check)

        non_upstream_tasks.difference_update(upstream_tasks)

        # Trim off any tasks that don't have dependee/dependent tasks, nor a
        # superior task with dependee/dependent tasks. These aren't part of the
        # subsystem
        tasks_to_check = collections.deque(subgraph.hierarchy_graph().top_level_tasks())
        visited_tasks = set[UID]()
        while tasks_to_check:
            task_with_dependencies_to_check = tasks_to_check.popleft()

            if task_with_dependencies_to_check not in non_upstream_tasks:
                continue

            if task_with_dependencies_to_check in visited_tasks:
                continue
            visited_tasks.add(task_with_dependencies_to_check)

            if not subgraph.dependency_graph().is_isolated(
                task_with_dependencies_to_check
            ):
                continue

            # Get a concrete copy of the subtasks, as you'll be removing
            # hierarchies and don't want to modify what you're iterating over
            for subtask in list(
                subgraph.hierarchy_graph().subtasks(task_with_dependencies_to_check)
            ):
                subgraph.remove_hierarchy(task_with_dependencies_to_check, subtask)
                if subgraph.hierarchy_graph().is_top_level(subtask):
                    tasks_to_check.append(subtask)
            subgraph.remove_task(task_with_dependencies_to_check)

            non_upstream_tasks.remove(task_with_dependencies_to_check)

        return subgraph, non_upstream_tasks

    def upstream_subgraph_multi(
        self, tasks: Iterable[UID], /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of all tasks upstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't upstream
        of any of the tasks, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks and are returned along
        with the subgraph.
        """
        # TODO: Make this more efficient - currently horrible
        combined_subgraph = NetworkGraph.empty()
        combined_non_upstream_tasks = set[UID]()
        for task in tasks:
            subgraph, non_upstream_tasks = self.upstream_subgraph(task)
            combined_subgraph.update(subgraph)

            combined_non_upstream_tasks.difference_update(subgraph.tasks())
            combined_non_upstream_tasks.update(non_upstream_tasks)

        return combined_subgraph, combined_non_upstream_tasks

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of tasks between the source task and target task.

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

        non_connecting_tasks = (
            non_downstream_tasks | non_upstream_tasks
        ) & target_upstream_subgraph.tasks()
        return target_upstream_subgraph, non_connecting_tasks

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of tasks between the source tasks and target tasks.

        All target tasks must be downstream of at least one of the source tasks.
        """
        source_tasks = list(source_tasks)
        target_tasks = list(target_tasks)

        for task in itertools.chain(source_tasks, target_tasks):
            if task not in self.tasks():
                raise TaskDoesNotExistError(task=task)

        sources_downstream_subgraph, non_downstream_tasks = (
            self.downstream_subgraph_multi(source_tasks)
        )
        try:
            (
                targets_upstream_subgraph,
                non_upstream_tasks,
            ) = sources_downstream_subgraph.upstream_subgraph_multi(target_tasks)
        except TaskDoesNotExistError as e:
            raise NoConnectingMultiSubgraphError(
                source_tasks=set(source_tasks), target_tasks=set(target_tasks)
            ) from e

        non_connecting_tasks = (
            non_downstream_tasks | non_upstream_tasks
        ) & targets_upstream_subgraph.tasks()
        return targets_upstream_subgraph, non_connecting_tasks

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

    def component(self, task: UID, /) -> NetworkGraph:
        """Return subgraph of all tasks in the same connected component as task."""
        subgraph = NetworkGraph.empty()

        if task not in self.tasks():
            raise TaskDoesNotExistError(task=task)

        checked_tasks = set[UID]()
        tasks_to_check = collections.deque([task])

        while tasks_to_check:
            task = tasks_to_check.popleft()

            if task in checked_tasks:
                continue
            checked_tasks.add(task)

            if task not in subgraph.tasks():
                subgraph.add_task(task)

            for dependee_task in self.dependency_graph().dependee_tasks(task):
                if dependee_task not in subgraph.tasks():
                    subgraph.add_task(dependee_task)
                if (
                    dependee_task,
                    task,
                ) not in subgraph.dependency_graph().dependencies():
                    subgraph.add_dependency(dependee_task, task)
                tasks_to_check.append(dependee_task)

            for dependent_task in self.dependency_graph().dependent_tasks(task):
                if dependent_task not in subgraph.tasks():
                    subgraph.add_task(dependent_task)
                if (
                    task,
                    dependent_task,
                ) not in subgraph.dependency_graph().dependencies():
                    subgraph.add_dependency(task, dependent_task)
                tasks_to_check.append(dependent_task)

            for supertask in self.hierarchy_graph().supertasks(task):
                if supertask not in subgraph.tasks():
                    subgraph.add_task(supertask)
                if (supertask, task) not in subgraph.hierarchy_graph().hierarchies():
                    subgraph.add_hierarchy(supertask, task)
                tasks_to_check.append(supertask)

            for subtask in self.hierarchy_graph().subtasks(task):
                if subtask not in subgraph.tasks():
                    subgraph.add_task(subtask)
                if (task, subtask) not in subgraph.hierarchy_graph().hierarchies():
                    subgraph.add_hierarchy(task, subtask)
                tasks_to_check.append(subtask)

        return subgraph

    def components(self) -> Generator[NetworkGraph, None, None]:
        """Return generator of connected components."""
        components = list[NetworkGraph]()
        for task in self.tasks():
            if any(task in component.tasks() for component in components):
                continue

            component = self.component(task)
            components.append(component)
            yield component


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

    def tasks(self) -> TasksView:
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

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> tuple[NetworkGraph, set[UID]]:
        """Return subgraph of tasks between source and target tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the source, nor upstream of the target, but are required to connect
        the two. I'm calling these non-connecting tasks.
        """
        return self._graph.connecting_subgraph(source_task, target_task)

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._graph.isolated_tasks()
