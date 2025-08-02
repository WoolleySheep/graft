from __future__ import annotations

import collections
import copy
import itertools
from typing import TYPE_CHECKING, Any, Protocol

from graft.domain.tasks.dependency_graph import (
    DependencyDoesNotExistError,
    DependencyGraph,
    DependencyGraphView,
    DependencySubgraphBuilder,
)
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.hierarchy_graph import (
    HierarchyDoesNotExistError,
    HierarchyGraph,
    HierarchyGraphView,
    HierarchySubgraphBuilder,
)
from graft.domain.tasks.uid import UID
from graft.utils import (
    LazyContainer,
    LazyFrozenSet,
    LazyTuple,
    unique,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable

    from graft.domain.tasks.uid import TasksView


class HasNeighboursError(Exception):
    """Raised when a task has neighbours.

    A task cannot be removed when it has any neighbours.
    """

    def __init__(
        self,
        task: UID,
        dependee_tasks: Iterable[UID],
        dependent_tasks: Iterable[UID],
        supertasks: Iterable[UID],
        subtasks: Iterable[UID],
    ) -> None:
        self.task = task
        self.dependee_tasks = set(dependee_tasks)
        self.dependent_tasks = set(dependent_tasks)
        self.supertasks = set(supertasks)
        self.subtasks = set(subtasks)
        formatted_neighbours = (
            str(neighbour)
            for neighbour in itertools.chain(
                self.dependee_tasks,
                self.dependent_tasks,
                self.supertasks,
                self.subtasks,
            )
        )
        super().__init__(
            f"Task [{task}] has neighbours [{', '.join(formatted_neighbours)}]"
        )


class DependencyIntroducesUnconstrainedNetworkCycleError(Exception):
    """Raised when adding the dependency introduces a cycle to the network graph."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: UnconstrainedNetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self._connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency from dependee-task [{dependee_task}] to dependent-task [{dependent_task}] introduces cycle into network graph",
            *args,
            **kwargs,
        )

    @property
    def connecting_subgraph(self) -> UnconstrainedNetworkGraph:
        return self._connecting_subgraph


class HierarchyIntroducesUnconstrainedNetworkCycleError(Exception):
    """Raised when adding the hierarchy introduces a cycle to the network graph."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: UnconstrainedNetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.supertask = supertask
        self.subtask = subtask
        self._connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Hierarchy from supertask [{supertask}] to subtask [{subtask}] introduces cycle into network graph",
            *args,
            **kwargs,
        )

    @property
    def connecting_subgraph(self) -> UnconstrainedNetworkGraph:
        return self._connecting_subgraph


class NoConnectingSubgraphError(Exception):
    """Raised when there is no connecting subsystem between two tasks."""

    def __init__(
        self,
        source_tasks: Iterable[UID],
        target_tasks: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise NoConnectingSubgraphError."""
        self.source_tasks = set(source_tasks)
        self.target_tasks = set(target_tasks)
        super().__init__(
            f"No connecting subgraph between tasks {source_tasks} and {target_tasks}.",
            *args,
            **kwargs,
        )


class IUnconstrainedNetworkGraphView(Protocol):
    """Interface for a view of an unconstrained task network graph."""

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        ...

    def __str__(self) -> str:
        """Return a string representation of the graph."""
        ...

    def clone(self) -> UnconstrainedNetworkGraph:
        """Return a clone of the graph."""
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

    def downstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        ...

    def downstream_tasks(self, tasks: Iterable[UID], /) -> Generator[UID, None, None]:
        """Yield tasks downstream of the given tasks."""
        ...

    def upstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        ...

    def upstream_tasks(self, tasks: Iterable[UID], /) -> Generator[UID, None, None]:
        """Yield tasks upstream of the given tasks."""
        ...

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> UnconstrainedNetworkGraph:
        """Return subgraph of tasks between source and target tasks.

        All targets must be reachable from at least one of the sources, or an error will
        be raised.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the source, nor upstream of the target, but are required to connect
        the two. I'm calling these non-connecting tasks.
        """
        ...

    def component_subgraph(self, task: UID, /) -> UnconstrainedNetworkGraph:
        """Return component subgraph containing the task."""
        ...

    def component_subgraphs(self) -> Generator[UnconstrainedNetworkGraph, None, None]:
        """Return each of the unique component subgraphs."""
        ...

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Yield isolated tasks."""
        ...


class UnconstrainedNetworkSubgraphBuilder:
    """Builder for a subgraph of an unconstrained network graph."""

    def __init__(self, graph: IUnconstrainedNetworkGraphView) -> None:
        self._graph = graph
        self._hierarchy_graph_builder = HierarchySubgraphBuilder(
            graph.hierarchy_graph()
        )
        self._dependency_graph_builder = DependencySubgraphBuilder(
            graph.dependency_graph()
        )

    def add_task(self, task: UID, /) -> None:
        if task not in self._graph.tasks():
            raise TaskDoesNotExistError(task)

        self._hierarchy_graph_builder.add_task(task)
        self._dependency_graph_builder.add_task(task)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        if (supertask, subtask) not in self._graph.hierarchy_graph().hierarchies():
            raise HierarchyDoesNotExistError(supertask=supertask, subtask=subtask)

        self._hierarchy_graph_builder.add_hierarchy(
            supertask=supertask, subtask=subtask
        )
        self._dependency_graph_builder.add_task(supertask)
        self._dependency_graph_builder.add_task(subtask)

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        if (
            dependee_task,
            dependent_task,
        ) not in self._graph.dependency_graph().dependencies():
            raise DependencyDoesNotExistError(
                dependee_task=dependee_task, dependent_task=dependent_task
            )

        self._dependency_graph_builder.add_dependency(
            dependee_task=dependee_task, dependent_task=dependent_task
        )
        self._hierarchy_graph_builder.add_task(dependee_task)
        self._hierarchy_graph_builder.add_task(dependent_task)

    def add_superior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        added_tasks = self._hierarchy_graph_builder.add_superior_subgraph(
            tasks,
            stop_condition=stop_condition,
        )
        for task in added_tasks:
            self._dependency_graph_builder.add_task(task)

        return added_tasks

    def add_inferior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        added_tasks = self._hierarchy_graph_builder.add_inferior_subgraph(
            tasks,
            stop_condition=stop_condition,
        )
        for task in added_tasks:
            self._dependency_graph_builder.add_task(task)

        return added_tasks

    def add_hierarchy_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        added_tasks = self._hierarchy_graph_builder.add_connecting_subgraph(
            source_tasks=source_tasks, target_tasks=target_tasks
        )
        for task in added_tasks:
            self._dependency_graph_builder.add_task(task)

        return added_tasks

    def add_hierarchy_component_subgraph(self, task: UID) -> set[UID]:
        added_tasks = self._hierarchy_graph_builder.add_component_subgraph(task)
        for task in added_tasks:
            self._dependency_graph_builder.add_task(task)
        return added_tasks

    def add_proceeding_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        added_tasks = self._dependency_graph_builder.add_proceeding_subgraph(
            tasks,
            stop_condition=stop_condition,
        )
        for task in added_tasks:
            self._hierarchy_graph_builder.add_task(task)

        return added_tasks

    def add_following_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        added_tasks = self._dependency_graph_builder.add_following_subgraph(
            tasks,
            stop_condition=stop_condition,
        )
        for task in added_tasks:
            self._hierarchy_graph_builder.add_task(task)

        return added_tasks

    def add_dependency_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        added_tasks = self._dependency_graph_builder.add_connecting_subgraph(
            source_tasks=source_tasks, target_tasks=target_tasks
        )
        for task in added_tasks:
            self._hierarchy_graph_builder.add_task(task)

        return added_tasks

    def add_dependency_component_subgraph(self, task: UID) -> set[UID]:
        added_tasks = self._dependency_graph_builder.add_component_subgraph(task)
        for task in added_tasks:
            self._hierarchy_graph_builder.add_task(task)
        return added_tasks

    def add_upstream_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        tasks_ = LazyTuple(tasks)
        for task in tasks_:
            if task not in self._graph.tasks():
                raise TaskDoesNotExistError(task)

        for task in tasks_:
            self.add_task(task)

        tasks_with_dependees_to_check = collections.deque[UID](tasks_)
        tasks_with_supertasks_to_check = collections.deque[UID](tasks_)
        tasks_with_subtasks_to_check = collections.deque[UID]()

        tasks_with_checked_dependees = set[UID]()
        tasks_with_checked_subtasks = set[UID]()
        tasks_with_checked_supertasks = set[UID]()

        tasks_with_dependee_tasks = collections.deque[UID]()
        potential_supertask_hierarchies = collections.defaultdict[UID, set[UID]](set)

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

                if self._graph.dependency_graph().dependee_tasks(
                    task_with_dependees_to_check
                ):
                    tasks_with_dependee_tasks.append(task_with_dependees_to_check)

                for dependee_task in self._graph.dependency_graph().dependee_tasks(
                    task_with_dependees_to_check
                ):
                    tasks_with_dependees_to_check.append(dependee_task)
                    tasks_with_subtasks_to_check.append(dependee_task)
                    tasks_with_supertasks_to_check.append(dependee_task)

                    self.add_dependency(dependee_task, task_with_dependees_to_check)

            while tasks_with_subtasks_to_check:
                task_with_subtasks_to_check = tasks_with_subtasks_to_check.popleft()

                if task_with_subtasks_to_check in tasks_with_checked_subtasks:
                    continue
                tasks_with_checked_subtasks.add(task_with_subtasks_to_check)

                for subtask in self._graph.hierarchy_graph().subtasks(
                    task_with_subtasks_to_check
                ):
                    tasks_with_dependees_to_check.append(subtask)
                    tasks_with_subtasks_to_check.append(subtask)
                    tasks_with_supertasks_to_check.append(subtask)

                    self.add_hierarchy(task_with_subtasks_to_check, subtask)

            while tasks_with_supertasks_to_check:
                task_with_supertasks_to_check = tasks_with_supertasks_to_check.popleft()

                if task_with_supertasks_to_check in tasks_with_checked_supertasks:
                    continue
                tasks_with_checked_supertasks.add(task_with_supertasks_to_check)

                for supertask in self._graph.hierarchy_graph().supertasks(
                    task_with_supertasks_to_check
                ):
                    tasks_with_dependees_to_check.append(supertask)
                    tasks_with_supertasks_to_check.append(supertask)

                    potential_supertask_hierarchies[supertask].add(
                        task_with_supertasks_to_check
                    )

        connecting_supertasks_to_check = tasks_with_dependee_tasks
        connecting_supertasks_checked = set[UID]()
        while connecting_supertasks_to_check:
            supertask = connecting_supertasks_to_check.popleft()
            if (
                supertask in connecting_supertasks_checked
                or supertask not in potential_supertask_hierarchies
            ):
                continue
            connecting_supertasks_checked.add(supertask)

            for subtask in potential_supertask_hierarchies[supertask]:
                self.add_hierarchy(supertask, subtask)
                connecting_supertasks_to_check.append(subtask)

        return tasks_with_checked_dependees.union(
            tasks_with_checked_subtasks,
            tasks_with_checked_supertasks,
            connecting_supertasks_checked,
        )

    def add_downstream_subgraph(self, tasks: Iterable[UID], /) -> set[UID]:
        tasks_ = LazyTuple(tasks)
        for task in tasks_:
            if task not in self._graph.tasks():
                raise TaskDoesNotExistError(task)

        for task in tasks_:
            self.add_task(task)

        tasks_with_dependents_to_check = collections.deque[UID](tasks_)
        tasks_with_supertasks_to_check = collections.deque[UID](tasks_)
        tasks_with_subtasks_to_check = collections.deque[UID]()

        tasks_with_checked_dependents = set[UID]()
        tasks_with_checked_subtasks = set[UID]()
        tasks_with_checked_supertasks = set[UID]()

        tasks_with_dependent_tasks = collections.deque[UID]()
        potential_supertask_hierarchies = collections.defaultdict[UID, set[UID]](set)

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

                if self._graph.dependency_graph().dependent_tasks(
                    task_with_dependents_to_check
                ):
                    tasks_with_dependent_tasks.append(task_with_dependents_to_check)

                for dependent_task in self._graph.dependency_graph().dependent_tasks(
                    task_with_dependents_to_check
                ):
                    tasks_with_dependents_to_check.append(dependent_task)
                    tasks_with_subtasks_to_check.append(dependent_task)
                    tasks_with_supertasks_to_check.append(dependent_task)

                    self.add_dependency(task_with_dependents_to_check, dependent_task)

            while tasks_with_subtasks_to_check:
                task_with_subtasks_to_check = tasks_with_subtasks_to_check.popleft()

                if task_with_subtasks_to_check in tasks_with_checked_subtasks:
                    continue
                tasks_with_checked_subtasks.add(task_with_subtasks_to_check)

                for subtask in self._graph.hierarchy_graph().subtasks(
                    task_with_subtasks_to_check
                ):
                    tasks_with_dependents_to_check.append(subtask)
                    tasks_with_subtasks_to_check.append(subtask)
                    tasks_with_supertasks_to_check.append(subtask)

                    self.add_hierarchy(task_with_subtasks_to_check, subtask)

            while tasks_with_supertasks_to_check:
                task_with_supertasks_to_check = tasks_with_supertasks_to_check.popleft()

                if task_with_supertasks_to_check in tasks_with_checked_supertasks:
                    continue
                tasks_with_checked_supertasks.add(task_with_supertasks_to_check)

                for supertask in self._graph.hierarchy_graph().supertasks(
                    task_with_supertasks_to_check
                ):
                    tasks_with_dependents_to_check.append(supertask)
                    tasks_with_supertasks_to_check.append(supertask)

                    potential_supertask_hierarchies[supertask].add(
                        task_with_supertasks_to_check
                    )

        connecting_supertasks_to_check = tasks_with_dependent_tasks
        connecting_supertasks_checked = set[UID]()
        while connecting_supertasks_to_check:
            supertask = connecting_supertasks_to_check.popleft()
            if (
                supertask in connecting_supertasks_checked
                or supertask not in potential_supertask_hierarchies
            ):
                continue
            connecting_supertasks_checked.add(supertask)

            for subtask in potential_supertask_hierarchies[supertask]:
                self.add_hierarchy(supertask, subtask)
                connecting_supertasks_to_check.append(subtask)

        return tasks_with_checked_dependents.union(
            tasks_with_checked_subtasks,
            tasks_with_checked_supertasks,
            connecting_supertasks_checked,
        )

    def add_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        # TODO: Make this implementation more efficient
        # Creates two intermediate graphs, can do better

        sources = LazyTuple(source_tasks)
        targets = LazyTuple(target_tasks)

        for task in itertools.chain(sources, targets):
            if task not in self._graph.tasks():
                raise TaskDoesNotExistError(task)

        source_downstream_subgraph = self._graph.downstream_subgraph(sources)

        if any(target not in source_downstream_subgraph.tasks() for target in targets):
            raise NoConnectingSubgraphError(sources, targets)

        connecting_subgraph = source_downstream_subgraph.upstream_subgraph(targets)

        for task in connecting_subgraph.tasks():
            self.add_task(task)

        for supertask, subtask in connecting_subgraph.hierarchy_graph().hierarchies():
            self.add_hierarchy(supertask, subtask)

        for (
            dependee_task,
            dependent_task,
        ) in connecting_subgraph.dependency_graph().dependencies():
            self.add_dependency(dependee_task, dependent_task)

        return set(connecting_subgraph.tasks())

    def add_component_subgraph(self, task: UID, /) -> set[UID]:
        if task not in self._graph.tasks():
            raise TaskDoesNotExistError(task=task)

        checked_tasks = set[UID]()
        tasks_to_check = collections.deque([task])

        self.add_task(task)

        while tasks_to_check:
            task = tasks_to_check.popleft()

            if task in checked_tasks:
                continue
            checked_tasks.add(task)

            for dependee_task in self._graph.dependency_graph().dependee_tasks(task):
                self.add_dependency(dependee_task, task)
                tasks_to_check.append(dependee_task)

            for dependent_task in self._graph.dependency_graph().dependent_tasks(task):
                self.add_dependency(task, dependent_task)
                tasks_to_check.append(dependent_task)

            for supertask in self._graph.hierarchy_graph().supertasks(task):
                self.add_hierarchy(supertask, task)
                tasks_to_check.append(supertask)

            for subtask in self._graph.hierarchy_graph().subtasks(task):
                self.add_hierarchy(task, subtask)
                tasks_to_check.append(subtask)

        return checked_tasks

    def add_all(self) -> set[UID]:
        for task in self._graph.tasks():
            self.add_task(task)
        for supertask, subtask in self._graph.hierarchy_graph().hierarchies():
            self.add_hierarchy(supertask=supertask, subtask=subtask)
        for (
            dependee_task,
            dependent_task,
        ) in self._graph.dependency_graph().dependencies():
            self.add_dependency(
                dependee_task=dependee_task, dependent_task=dependent_task
            )
        return set(self._graph.tasks())

    def build(self) -> UnconstrainedNetworkGraph:
        dependency_graph = self._dependency_graph_builder.build()
        hierarchy_graph = self._hierarchy_graph_builder.build()
        return UnconstrainedNetworkGraph(
            dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
        )


class UnconstrainedNetworkGraph:
    """Graph combining task hierarchies and dependencies."""

    @classmethod
    def empty(cls) -> UnconstrainedNetworkGraph:
        """Create an empty network graph."""
        return cls(DependencyGraph(), HierarchyGraph())

    def __init__(
        self, dependency_graph: DependencyGraph, hierarchy_graph: HierarchyGraph
    ) -> None:
        """Initialise UnconstrainedNetworkGraph."""
        # TODO: Note that this approach does not guarantee that the resultant
        # UnconstrainedNetworkGraph is valid; more validation will need to be done to ensure
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
        if not isinstance(other, UnconstrainedNetworkGraph):
            return NotImplemented

        return (
            self.dependency_graph() == other.dependency_graph()
            and self.hierarchy_graph() == other.hierarchy_graph()
        )

    def __str__(self) -> str:
        """Return a string representation of the graph."""
        frozen_hierarchy_graph = frozenset(
            (task, frozenset(self._hierarchy_graph.subtasks(task)))
            for task in self.tasks()
        )
        frozen_dependency_graph = frozenset(
            (task, frozenset(self._dependency_graph.dependent_tasks(task)))
            for task in self.tasks()
        )
        network_hash = hash((frozen_hierarchy_graph, frozen_dependency_graph))
        return f"UnconstrainedNetworkGraph({network_hash})"

    def __repr__(self) -> str:
        """Return a string representation of the graph."""
        return str(self)

    def clone(self) -> UnconstrainedNetworkGraph:
        """Return a clone of the graph."""
        return copy.deepcopy(self)

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
        if not self._dependency_graph.is_isolated(
            task
        ) or not self._hierarchy_graph.is_isolated(task):
            raise HasNeighboursError(
                task=task,
                dependee_tasks=self._dependency_graph.dependee_tasks(task),
                dependent_tasks=self._dependency_graph.dependent_tasks(task),
                supertasks=self._hierarchy_graph.supertasks(task),
                subtasks=self._hierarchy_graph.subtasks(task),
            )

        self._dependency_graph.validate_task_can_be_removed(task)
        self._hierarchy_graph.validate_task_can_be_removed(task)

    def remove_task(self, task: UID, /) -> None:
        """Remove a task from the graph."""
        self.validate_task_can_be_removed(task)

        self._hierarchy_graph.remove_task(task)
        self._dependency_graph.remove_task(task)

    def validate_hierarchy_can_be_added(self, supertask: UID, subtask: UID, /) -> None:
        """Validate that hierarchy can be added to the graph."""

        def has_network_cycle_with_supertask_upstream_of_subtask_or_its_inferior_tasks(
            supertask: UID, subtask: UID
        ) -> bool:
            """Check if there is a network cycle.

            Aka: Check if there is a stream path from the supertask to the subtask or
            any of the subtask's inferiors
            """
            subtask_and_its_inferior_tasks = LazyContainer(
                itertools.chain(
                    [subtask], self._hierarchy_graph.inferior_tasks([subtask])
                )
            )
            return any(
                task in subtask_and_its_inferior_tasks
                for task in itertools.chain(
                    [supertask], self.downstream_tasks([supertask])
                )
            )

        def has_network_cycle_with_subtask_or_its_inferior_tasks_upstream_of_supertask(
            supertask: UID, subtask: UID
        ) -> bool:
            """Check if there is a network cycle.

            Aka: Check if there is a stream path from the subtask or any subtasks's
            inferiors to the supertask
            """
            subtask_and_its_inferior_tasks = LazyContainer(
                itertools.chain(
                    [subtask], self._hierarchy_graph.inferior_tasks([subtask])
                )
            )
            return any(
                task in subtask_and_its_inferior_tasks
                for task in itertools.chain(
                    [supertask], self.upstream_tasks([supertask])
                )
            )

        self._hierarchy_graph.validate_hierarchy_can_be_added(supertask, subtask)

        if has_network_cycle_with_supertask_upstream_of_subtask_or_its_inferior_tasks(
            supertask=supertask, subtask=subtask
        ):
            subtask_and_its_inferior_tasks = LazyFrozenSet(
                itertools.chain(
                    [subtask], self.hierarchy_graph().inferior_tasks([subtask])
                )
            )
            supertask_downstream_subgraph = self.downstream_subgraph([supertask])
            supertask_and_its_downstream_tasks = itertools.chain(
                [supertask], supertask_downstream_subgraph.downstream_tasks([supertask])
            )
            intersecting_tasks = [
                task
                for task in supertask_and_its_downstream_tasks
                if task in subtask_and_its_inferior_tasks
                and (
                    supertask_downstream_subgraph.dependency_graph().dependee_tasks(
                        task
                    )
                    or not (
                        supertask_downstream_subgraph.hierarchy_graph().supertasks(task)
                        <= subtask_and_its_inferior_tasks
                    )
                )
            ]

            builder = UnconstrainedNetworkSubgraphBuilder(self)
            builder.add_connecting_subgraph([supertask], intersecting_tasks)
            builder.add_hierarchy_connecting_subgraph([subtask], intersecting_tasks)

            raise HierarchyIntroducesUnconstrainedNetworkCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
            )

        if has_network_cycle_with_subtask_or_its_inferior_tasks_upstream_of_supertask(
            supertask=supertask, subtask=subtask
        ):
            subtask_and_its_inferior_tasks = LazyFrozenSet(
                itertools.chain(
                    [subtask], self.hierarchy_graph().inferior_tasks([subtask])
                )
            )
            upstream_subgraph_of_supertask = self.upstream_subgraph([supertask])
            supertask_and_its_upstream_tasks = itertools.chain(
                [supertask], upstream_subgraph_of_supertask.upstream_tasks([supertask])
            )
            intersecting_tasks = [
                task
                for task in supertask_and_its_upstream_tasks
                if task in subtask_and_its_inferior_tasks
                and (
                    upstream_subgraph_of_supertask.dependency_graph().dependent_tasks(
                        task
                    )
                    or not (
                        upstream_subgraph_of_supertask.hierarchy_graph().supertasks(
                            task
                        )
                        <= subtask_and_its_inferior_tasks
                    )
                )
            ]

            builder = UnconstrainedNetworkSubgraphBuilder(self)
            builder.add_connecting_subgraph(intersecting_tasks, [supertask])
            builder.add_hierarchy_connecting_subgraph([subtask], intersecting_tasks)

            raise HierarchyIntroducesUnconstrainedNetworkCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
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

        def has_network_cycle_with_dependent_task_or_its_inferior_task_upstream_of_dependee_task_or_its_inferior_task(
            dependee_task: UID, dependent_task: UID
        ) -> bool:
            dependee_task_and_its_inferior_tasks = LazyContainer(
                itertools.chain(
                    [dependee_task],
                    self._hierarchy_graph.inferior_tasks([dependee_task]),
                )
            )
            dependent_task_and_its_inferior_tasks = itertools.chain(
                [dependent_task], self._hierarchy_graph.inferior_tasks([dependent_task])
            )
            (
                dependent_task_and_its_inferior_tasks1,
                dependent_task_and_its_inferior_tasks2,
            ) = itertools.tee(dependent_task_and_its_inferior_tasks)
            dependent_task_and_its_inferior_tasks_and_their_downstream_tasks = unique(
                itertools.chain(
                    dependent_task_and_its_inferior_tasks1,
                    self.downstream_tasks(dependent_task_and_its_inferior_tasks2),
                )
            )
            return any(
                task in dependee_task_and_its_inferior_tasks
                for task in dependent_task_and_its_inferior_tasks_and_their_downstream_tasks
            )

        self._dependency_graph.validate_dependency_can_be_added(
            dependee_task, dependent_task
        )

        # TODO: Work out how to merge these two network cycle checks into the later one.
        # I've tried without success, it's just hard.
        if dependent_task in self._hierarchy_graph.inferior_tasks([dependee_task]):
            builder = UnconstrainedNetworkSubgraphBuilder(self)
            _ = builder.add_hierarchy_connecting_subgraph(
                [dependee_task], [dependent_task]
            )
            raise DependencyIntroducesUnconstrainedNetworkCycleError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

        if dependee_task in self._hierarchy_graph.inferior_tasks([dependent_task]):
            builder = UnconstrainedNetworkSubgraphBuilder(self)
            _ = builder.add_hierarchy_connecting_subgraph(
                [dependent_task], [dependee_task]
            )
            raise DependencyIntroducesUnconstrainedNetworkCycleError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

        if has_network_cycle_with_dependent_task_or_its_inferior_task_upstream_of_dependee_task_or_its_inferior_task(
            dependee_task=dependee_task, dependent_task=dependent_task
        ):
            dependent_task_and_its_inferior_tasks = {
                dependent_task,
                *self._hierarchy_graph.inferior_tasks([dependent_task]),
            }

            dependent_task_and_its_inferior_tasks_downstream_subgraph = (
                self.downstream_subgraph(dependent_task_and_its_inferior_tasks)
            )
            dependent_task_and_its_inferior_tasks_and_their_downstream_tasks = unique(
                itertools.chain(
                    dependent_task_and_its_inferior_tasks,
                    dependent_task_and_its_inferior_tasks_downstream_subgraph.downstream_tasks(
                        dependent_task_and_its_inferior_tasks
                    ),
                )
            )

            dependee_task_and_its_inferior_tasks = LazyFrozenSet(
                itertools.chain(
                    [dependee_task],
                    self._hierarchy_graph.inferior_tasks([dependee_task]),
                )
            )

            intersecting_dependee_task_and_its_inferior_tasks = [
                task
                for task in dependent_task_and_its_inferior_tasks_and_their_downstream_tasks
                if task in dependee_task_and_its_inferior_tasks
                and (
                    dependent_task_and_its_inferior_tasks_downstream_subgraph.dependency_graph().dependee_tasks(
                        task
                    )
                    or not (
                        dependent_task_and_its_inferior_tasks_downstream_subgraph.hierarchy_graph().supertasks(
                            task
                        )
                        <= dependee_task_and_its_inferior_tasks
                    )
                )
            ]

            intersecting_dependee_tasks_and_its_inferiors_upstream_subgraph = dependent_task_and_its_inferior_tasks_downstream_subgraph.upstream_subgraph(
                intersecting_dependee_task_and_its_inferior_tasks
            )
            intersecting_dependee_tasks_and_its_inferiors_and_their_upstream_tasks = unique(
                itertools.chain(
                    intersecting_dependee_task_and_its_inferior_tasks,
                    intersecting_dependee_tasks_and_its_inferiors_upstream_subgraph.upstream_tasks(
                        intersecting_dependee_task_and_its_inferior_tasks
                    ),
                )
            )

            intersecting_dependent_task_and_its_inferior_tasks = [
                task
                for task in intersecting_dependee_tasks_and_its_inferiors_and_their_upstream_tasks
                if task in dependent_task_and_its_inferior_tasks
                and (
                    intersecting_dependee_tasks_and_its_inferiors_upstream_subgraph.dependency_graph().dependent_tasks(
                        task
                    )
                    or not (
                        intersecting_dependee_tasks_and_its_inferiors_upstream_subgraph.hierarchy_graph().supertasks(
                            task
                        )
                        <= dependent_task_and_its_inferior_tasks
                    )
                )
            ]

            builder = UnconstrainedNetworkSubgraphBuilder(self)
            builder.add_connecting_subgraph(
                intersecting_dependent_task_and_its_inferior_tasks,
                intersecting_dependee_task_and_its_inferior_tasks,
            )
            builder.add_hierarchy_connecting_subgraph(
                [dependent_task], intersecting_dependent_task_and_its_inferior_tasks
            )
            builder.add_hierarchy_connecting_subgraph(
                [dependee_task], intersecting_dependee_task_and_its_inferior_tasks
            )

            raise DependencyIntroducesUnconstrainedNetworkCycleError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Add a dependency between the specified tasks."""
        self.validate_dependency_can_be_added(dependee_task, dependent_task)
        self._dependency_graph.add_dependency(dependee_task, dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the specified dependency."""
        self._dependency_graph.remove_dependency(dependee_task, dependent_task)

    def downstream_tasks(self, tasks: Iterable[UID]) -> Generator[UID, None, None]:
        """Return tasks downstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        tasks1, tasks2 = itertools.tee(tasks)

        downstream_tasks_to_check = collections.deque(
            unique(
                itertools.chain.from_iterable(
                    map(self._dependency_graph.dependent_tasks, tasks1)
                )
            )
        )
        supertasks_to_check = collections.deque(
            unique(
                itertools.chain.from_iterable(
                    map(self._hierarchy_graph.supertasks, tasks2)
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

    def upstream_tasks(self, tasks: Iterable[UID], /) -> Generator[UID, None, None]:
        """Return tasks upstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        tasks1, tasks2 = itertools.tee(tasks)

        upstream_tasks_to_check = collections.deque(
            itertools.chain.from_iterable(
                map(self._dependency_graph.dependee_tasks, tasks1)
            )
        )
        supertasks_to_check = collections.deque(
            itertools.chain.from_iterable(map(self._hierarchy_graph.supertasks, tasks2))
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

    def downstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all tasks downstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of any of the tasks, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        builder = UnconstrainedNetworkSubgraphBuilder(self)
        builder.add_downstream_subgraph(tasks)
        return builder.build()

    def upstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all tasks upstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't upstream
        of any of the tasks, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks and are returned along
        with the subgraph.
        """
        builder = UnconstrainedNetworkSubgraphBuilder(self)
        builder.add_upstream_subgraph(tasks)
        return builder.build()

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> UnconstrainedNetworkGraph:
        """Return subgraph of tasks between the source tasks and target tasks.

        All target tasks must be downstream of at least one of the source tasks.
        """
        builder = UnconstrainedNetworkSubgraphBuilder(self)
        builder.add_connecting_subgraph(source_tasks, target_tasks)
        return builder.build()

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

    def component_subgraph(self, task: UID, /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all tasks in the same connected component as task."""
        builder = UnconstrainedNetworkSubgraphBuilder(self)
        builder.add_component_subgraph(task)
        return builder.build()

    def component_subgraphs(self) -> Generator[UnconstrainedNetworkGraph, None, None]:
        """Return generator of connected components."""
        checked_tasks = set[UID]()
        for node in self.tasks():
            if node in checked_tasks:
                continue

            component = self.component_subgraph(node)
            checked_tasks.update(component.tasks())
            yield component


class UnconstrainedNetworkGraphView:
    """View of Network Graph."""

    def __init__(self, graph: IUnconstrainedNetworkGraphView) -> None:
        """Initialise UnconstrainedNetworkGraphView."""
        self._graph = graph

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._graph)

    def __eq__(self, other: object) -> bool:
        """Check if graph views are equal."""
        return (
            isinstance(other, UnconstrainedNetworkGraphView)
            and self.hierarchy_graph() == other.hierarchy_graph()
            and self.dependency_graph() == other.dependency_graph()
        )

    def clone(self) -> UnconstrainedNetworkGraph:
        """Return a clone of the graph."""
        return self._graph.clone()

    def tasks(self) -> TasksView:
        """Return a view of the tasks in the graph."""
        return self._graph.tasks()

    def hierarchy_graph(self) -> HierarchyGraphView:
        """Return a view of the hierarchy graph."""
        return self._graph.hierarchy_graph()

    def dependency_graph(self) -> DependencyGraphView:
        """Return a view of the dependency graph."""
        return self._graph.dependency_graph()

    def downstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        return self._graph.downstream_subgraph(tasks)

    def downstream_tasks(self, tasks: Iterable[UID]) -> Generator[UID, None, None]:
        """Return tasks downstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self._graph.downstream_tasks(tasks)

    def upstream_subgraph(self, tasks: Iterable[UID], /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all upstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't upstream
        of the task, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks.
        """
        return self._graph.upstream_subgraph(tasks)

    def upstream_tasks(self, tasks: Iterable[UID], /) -> Generator[UID, None, None]:
        """Return tasks upstream of any of the tasks.

        The order of task yielding is neither breadth-first or depth-first - it
        just is what it is.
        """
        return self._graph.upstream_tasks(tasks)

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> UnconstrainedNetworkGraph:
        """Return subgraph of tasks between the source tasks and target tasks.

        All target tasks must be downstream of at least one of the source tasks.
        """
        return self._graph.connecting_subgraph(source_tasks, target_tasks)

    def component_subgraph(self, task: UID, /) -> UnconstrainedNetworkGraph:
        """Return subgraph of all tasks in the same connected component as task."""
        return self._graph.component_subgraph(task)

    def component_subgraphs(self) -> Generator[UnconstrainedNetworkGraph, None, None]:
        """Return generator of connected components."""
        return self._graph.component_subgraphs()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._graph.isolated_tasks()
