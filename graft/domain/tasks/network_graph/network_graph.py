from __future__ import annotations

import collections
import copy
import itertools
from typing import TYPE_CHECKING, Any, Protocol, Self, override

from graft.domain.tasks.dependency_graph import (
    DependencyGraph,
    DependencySubgraphBuilder,
)
from graft.domain.tasks.hierarchy_graph import (
    HierarchyGraph,
    HierarchySubgraphBuilder,
)
from graft.domain.tasks.network_graph.unconstrained_network_graph import (
    DependencyIntroducesUnconstrainedNetworkCycleError,
    HierarchyIntroducesUnconstrainedNetworkCycleError,
    UnconstrainedNetworkGraph,
    UnconstrainedNetworkSubgraphBuilder,
)
from graft.domain.tasks.uid import UID
from graft.utils import (
    CheckableIterable,
    LazyContainer,
    unique,
)

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from graft.domain.tasks.dependency_graph import (
        DependencyGraphView,
    )
    from graft.domain.tasks.hierarchy_graph import (
        HierarchyGraphView,
    )
    from graft.domain.tasks.uid import TasksView


class DependencyIntroducesNetworkCycleError(
    DependencyIntroducesUnconstrainedNetworkCycleError
):
    """Raised when adding the dependency introduces a cycle to the network graph."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(
            dependee_task,
            dependent_task,
            connecting_subgraph,
            *args,
            **kwargs,
        )
        self._connecting_subgraph = connecting_subgraph

    @property
    def connecting_subgraph(self) -> NetworkGraph:
        return self._connecting_subgraph


class HierarchyIntroducesNetworkCycleError(
    HierarchyIntroducesUnconstrainedNetworkCycleError
):
    """Raised when adding the hierarchy introduces a cycle to the network graph."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: NetworkGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(supertask, subtask, connecting_subgraph, *args, **kwargs)
        self._connecting_subgraph = connecting_subgraph

    @property
    def connecting_subgraph(self) -> NetworkGraph:
        return self._connecting_subgraph


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


class INetworkGraphView(Protocol):
    """Interface for a view of a task network graph."""

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        ...

    def __str__(self) -> str:
        """Return a string representation of the graph."""
        ...

    def clone(self) -> NetworkGraph:
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

    def downstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
        """Return subgraph of all downstream tasks of task.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the task, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        ...

    def downstream_tasks(self, tasks: Iterable[UID], /) -> Generator[UID, None, None]:
        """Yield tasks downstream of the given tasks."""
        ...

    def upstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
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
    ) -> NetworkGraph:
        """Return subgraph of tasks between source and target tasks.

        All targets must be reachable from at least one of the sources, or an error will
        be raised.

        Note that the subgraph will contain a few tasks that aren't downstream
        of the source, nor upstream of the target, but are required to connect
        the two. I'm calling these non-connecting tasks.
        """
        ...

    def component_subgraph(self, task: UID, /) -> NetworkGraph:
        """Return component subgraph containing the task."""
        ...

    def component_subgraphs(self) -> Generator[NetworkGraph, None, None]:
        """Return each of the unique component subgraphs."""
        ...

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Yield isolated tasks."""
        ...


class NetworkSubgraphBuilder(UnconstrainedNetworkSubgraphBuilder):
    """Builder for a subgraph of a network graph."""

    def __init__(self, graph: INetworkGraphView) -> None:
        self._graph = graph
        self._hierarchy_graph_builder = HierarchySubgraphBuilder(
            graph.hierarchy_graph()
        )
        self._dependency_graph_builder = DependencySubgraphBuilder(
            graph.dependency_graph()
        )

    @override
    def build(self) -> NetworkGraph:
        dependency_graph = self._dependency_graph_builder.build()
        hierarchy_graph = self._hierarchy_graph_builder.build()
        return NetworkGraph(
            dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
        )


class NetworkGraph(UnconstrainedNetworkGraph):
    """Graph combining task hierarchies and dependencies."""

    @classmethod
    def empty(cls) -> NetworkGraph:
        """Create an empty network graph."""
        return cls(DependencyGraph(), HierarchyGraph())

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        if not isinstance(other, NetworkGraph):
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
        return f"NetworkGraph({network_hash})"

    def __repr__(self) -> str:
        """Return a string representation of the graph."""
        return str(self)

    @override
    def clone(self) -> NetworkGraph:
        """Return a clone of the graph."""
        return copy.deepcopy(self)

    @override
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
            supertask_and_its_superior_tasks = itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks([supertask])
            )
            tasks_a_single_step_upstream_of_the_supertask = CheckableIterable(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._dependency_graph.dependee_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            if not tasks_a_single_step_upstream_of_the_supertask:
                return False

            (
                tasks_a_single_step_upstream_of_the_supertask1,
                tasks_a_single_step_upstream_of_the_supertask2,
            ) = itertools.tee(tasks_a_single_step_upstream_of_the_supertask)

            tasks_a_single_step_upstream_of_the_supertask_and_their_inferior_tasks = (
                LazyContainer(
                    itertools.chain(
                        tasks_a_single_step_upstream_of_the_supertask1,
                        self._hierarchy_graph.inferior_tasks(
                            tasks_a_single_step_upstream_of_the_supertask2
                        ),
                    )
                )
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks([subtask])
            )
            dependee_tasks_of_subtask_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )
            return any(
                dependee_task
                in tasks_a_single_step_upstream_of_the_supertask_and_their_inferior_tasks
                for dependee_task in dependee_tasks_of_subtask_and_its_inferior_tasks
            )

        def has_dependency_duplication_with_downstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are duplicate dependencies with a downstream hierarchy.

             Aka: Check if any of the tasks one step downstream of the supertask
            are superior-or-equal to any of the dependee-tasks of the (sub-task or
            inferior-tasks of the sub-task).
            """
            supertask_and_its_superior_tasks = itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks([supertask])
            )
            tasks_a_single_step_downstream_of_the_supertask = CheckableIterable(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._dependency_graph.dependent_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            if not tasks_a_single_step_downstream_of_the_supertask:
                return False

            (
                tasks_a_single_step_downstream_of_the_supertask1,
                tasks_a_single_step_downstream_of_the_supertask2,
            ) = itertools.tee(tasks_a_single_step_downstream_of_the_supertask)

            tasks_a_single_step_downstream_of_the_supertask_and_their_inferior_tasks = (
                LazyContainer(
                    itertools.chain(
                        tasks_a_single_step_downstream_of_the_supertask1,
                        self._hierarchy_graph.inferior_tasks(
                            tasks_a_single_step_downstream_of_the_supertask2
                        ),
                    )
                )
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks([subtask])
            )
            dependent_tasks_of_subtask_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )
            return any(
                dependent_task
                in tasks_a_single_step_downstream_of_the_supertask_and_their_inferior_tasks
                for dependent_task in dependent_tasks_of_subtask_and_its_inferior_tasks
            )

        def has_dependency_crossover_with_upstream_hierarchy(
            self: Self, supertask: UID, subtask: UID
        ) -> bool:
            """Check if there are any dependency crossovers with an upstream hierarchy.

            Check if any of the tasks one step upstream of the super-task are inferior
            to any of the dependee-tasks of the (sub-task or inferior-tasks of the
            sub-task).
            """
            supertask_and_its_superior_tasks = itertools.chain(
                [supertask], self._hierarchy_graph.superior_tasks([supertask])
            )
            tasks_a_single_step_upstream_of_the_supertask = CheckableIterable(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._dependency_graph.dependee_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            if not tasks_a_single_step_upstream_of_the_supertask:
                return False

            (
                tasks_a_single_step_upstream_of_the_supertask1,
                tasks_a_single_step_upstream_of_the_supertask2,
            ) = itertools.tee(tasks_a_single_step_upstream_of_the_supertask)

            superior_tasks_of_tasks_a_single_step_upstream_of_the_supertask = (
                LazyContainer(
                    itertools.chain(
                        tasks_a_single_step_upstream_of_the_supertask1,
                        self._hierarchy_graph.superior_tasks(
                            tasks_a_single_step_upstream_of_the_supertask2
                        ),
                    ),
                )
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks([subtask])
            )

            dependee_tasks_of_subtask_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            return any(
                task in superior_tasks_of_tasks_a_single_step_upstream_of_the_supertask
                for task in dependee_tasks_of_subtask_and_its_inferior_tasks
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
                [supertask], self._hierarchy_graph.superior_tasks([supertask])
            )
            tasks_a_single_step_downstream_of_the_supertask = CheckableIterable(
                unique(
                    itertools.chain.from_iterable(
                        map(
                            self._dependency_graph.dependent_tasks,
                            supertask_and_its_superior_tasks,
                        )
                    )
                )
            )

            if not tasks_a_single_step_downstream_of_the_supertask:
                return False

            (
                tasks_a_single_step_downstream_of_the_supertask1,
                tasks_a_single_step_downstream_of_the_supertask2,
            ) = itertools.tee(tasks_a_single_step_downstream_of_the_supertask)

            superior_tasks_of_tasks_a_single_step_downstream_of_the_supertask = (
                LazyContainer(
                    itertools.chain(
                        tasks_a_single_step_downstream_of_the_supertask1,
                        self._hierarchy_graph.superior_tasks(
                            tasks_a_single_step_downstream_of_the_supertask2
                        ),
                    ),
                )
            )

            subtask_and_its_inferior_tasks = itertools.chain(
                [subtask], self._hierarchy_graph.inferior_tasks([subtask])
            )

            dependent_tasks_of_subtask_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            return any(
                dependent_task_of_subtask_or_its_inferior_task
                in superior_tasks_of_tasks_a_single_step_downstream_of_the_supertask
                for dependent_task_of_subtask_or_its_inferior_task in dependent_tasks_of_subtask_and_its_inferior_tasks
            )

        try:
            super().validate_hierarchy_can_be_added(supertask, subtask)
        except HierarchyIntroducesUnconstrainedNetworkCycleError as e:
            hierarchy_graph = HierarchyGraph(
                (task, e.connecting_subgraph.hierarchy_graph().subtasks(task))
                for task in e.connecting_subgraph.hierarchy_graph().tasks()
            )
            dependency_graph = DependencyGraph(
                (task, e.connecting_subgraph.dependency_graph().dependent_tasks(task))
                for task in e.connecting_subgraph.dependency_graph().tasks()
            )
            connecting_subgraph = NetworkGraph(
                dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
            )
            raise HierarchyIntroducesNetworkCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            ) from None

        if has_dependency_duplication_with_upstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_and_its_superior_tasks = {
                supertask,
                *self._hierarchy_graph.superior_tasks([supertask]),
            }
            tasks_a_single_step_upstream_of_the_supertask = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            subtask_and_its_inferior_tasks = {
                subtask,
                *self._hierarchy_graph.inferior_tasks([subtask]),
            }

            dependee_tasks_of_either_subtask_or_its_inferior_tasks = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            tasks_a_single_step_upstream_of_the_supertask_inferior_subgraph = (
                self._hierarchy_graph.inferior_subgraph(
                    tasks_a_single_step_upstream_of_the_supertask
                )
            )

            intersecting_lower_tasks_in_upstream_hierarchy = (
                tasks_a_single_step_upstream_of_the_supertask_inferior_subgraph.tasks()
                & dependee_tasks_of_either_subtask_or_its_inferior_tasks
            )

            intersecting_lower_tasks_in_upstream_hierarchy_and_their_superior_tasks = (
                itertools.chain(
                    intersecting_lower_tasks_in_upstream_hierarchy,
                    self._hierarchy_graph.superior_tasks(
                        intersecting_lower_tasks_in_upstream_hierarchy
                    ),
                )
            )

            intersecting_upper_tasks_in_upstream_hierarchy = set(
                filter(
                    lambda task: task in tasks_a_single_step_upstream_of_the_supertask,
                    intersecting_lower_tasks_in_upstream_hierarchy_and_their_superior_tasks,
                )
            )

            cross_hierarchy_dependencies = list[tuple[UID, UID]]()

            intersecting_upper_tasks_in_new_hierarchy = list[UID]()
            for supertask_or_its_superior_task in supertask_and_its_superior_tasks:
                dependee_tasks_in_upstream_hierarchy = (
                    self._dependency_graph.dependee_tasks(
                        supertask_or_its_superior_task
                    )
                    & intersecting_upper_tasks_in_upstream_hierarchy
                )
                if not dependee_tasks_in_upstream_hierarchy:
                    continue
                intersecting_upper_tasks_in_new_hierarchy.append(
                    supertask_or_its_superior_task
                )
                for dependee_task in dependee_tasks_in_upstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (dependee_task, supertask_or_its_superior_task)
                    )

            intersecting_lower_tasks_in_new_hierarchy = list[UID]()
            for subtask_or_its_inferior_task in subtask_and_its_inferior_tasks:
                dependee_tasks_in_upstream_hierarchy = (
                    self._dependency_graph.dependee_tasks(subtask_or_its_inferior_task)
                    & intersecting_lower_tasks_in_upstream_hierarchy
                )
                if not dependee_tasks_in_upstream_hierarchy:
                    continue
                intersecting_lower_tasks_in_new_hierarchy.append(
                    subtask_or_its_inferior_task
                )
                for dependee_task in dependee_tasks_in_upstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (dependee_task, subtask_or_its_inferior_task)
                    )

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_new_hierarchy, [supertask]
            )
            builder.add_hierarchy_connecting_subgraph(
                [subtask], intersecting_lower_tasks_in_new_hierarchy
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_upstream_hierarchy,
                intersecting_lower_tasks_in_upstream_hierarchy,
            )
            for dependee_task, dependent_task in cross_hierarchy_dependencies:
                builder.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyDuplicationError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_duplication_with_downstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_and_its_superior_tasks = set(
                itertools.chain(
                    [supertask], self._hierarchy_graph.superior_tasks([supertask])
                )
            )
            tasks_a_single_step_downstream_of_the_supertask = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            subtask_and_its_inferior_tasks = set(
                itertools.chain(
                    [subtask], self._hierarchy_graph.inferior_tasks([subtask])
                )
            )

            dependent_tasks_of_either_subtask_or_its_inferior_tasks = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            tasks_a_single_step_downstream_of_the_supertask_inferior_subgraph = (
                self._hierarchy_graph.inferior_subgraph(
                    tasks_a_single_step_downstream_of_the_supertask
                )
            )

            intersecting_lower_tasks_in_downstream_hierarchy = (
                tasks_a_single_step_downstream_of_the_supertask_inferior_subgraph.tasks()
                & dependent_tasks_of_either_subtask_or_its_inferior_tasks
            )

            intersecting_lower_tasks_in_downstream_hierarchy_and_their_superior_tasks = itertools.chain(
                intersecting_lower_tasks_in_downstream_hierarchy,
                self._hierarchy_graph.superior_tasks(
                    intersecting_lower_tasks_in_downstream_hierarchy
                ),
            )

            intersecting_upper_tasks_in_downstream_hierarchy = set(
                filter(
                    lambda task: task
                    in tasks_a_single_step_downstream_of_the_supertask,
                    intersecting_lower_tasks_in_downstream_hierarchy_and_their_superior_tasks,
                )
            )

            cross_hierarchy_dependencies = list[tuple[UID, UID]]()

            intersecting_upper_tasks_in_new_hierarchy = list[UID]()
            for supertask_or_its_superior_task in supertask_and_its_superior_tasks:
                dependent_tasks_in_downstream_hierarchy = (
                    self._dependency_graph.dependent_tasks(
                        supertask_or_its_superior_task
                    )
                    & intersecting_upper_tasks_in_downstream_hierarchy
                )
                if not dependent_tasks_in_downstream_hierarchy:
                    continue
                intersecting_upper_tasks_in_new_hierarchy.append(
                    supertask_or_its_superior_task
                )
                for dependent_task in dependent_tasks_in_downstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (supertask_or_its_superior_task, dependent_task)
                    )

            intersecting_lower_tasks_in_new_hierarchy = list[UID]()
            for subtask_or_its_inferior_task in subtask_and_its_inferior_tasks:
                dependent_tasks_in_downstream_hierarchy = (
                    self._dependency_graph.dependent_tasks(subtask_or_its_inferior_task)
                    & intersecting_lower_tasks_in_downstream_hierarchy
                )
                if not dependent_tasks_in_downstream_hierarchy:
                    continue
                intersecting_lower_tasks_in_new_hierarchy.append(
                    subtask_or_its_inferior_task
                )
                for dependent_task in dependent_tasks_in_downstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (subtask_or_its_inferior_task, dependent_task)
                    )

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_new_hierarchy, [supertask]
            )
            builder.add_hierarchy_connecting_subgraph(
                [subtask], intersecting_lower_tasks_in_new_hierarchy
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_downstream_hierarchy,
                intersecting_lower_tasks_in_downstream_hierarchy,
            )
            for dependee_task, dependent_task in cross_hierarchy_dependencies:
                builder.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyDuplicationError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_crossover_with_upstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_and_its_superior_tasks = set(
                itertools.chain(
                    [supertask], self._hierarchy_graph.superior_tasks([supertask])
                )
            )
            tasks_a_single_step_upstream_of_the_supertask = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            subtask_and_its_inferior_tasks = set(
                itertools.chain(
                    [subtask], self._hierarchy_graph.inferior_tasks([subtask])
                )
            )

            dependee_tasks_of_either_subtask_or_its_inferior_tasks = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependee_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            tasks_a_single_step_upstream_of_the_supertask_superior_subgraph = (
                self._hierarchy_graph.superior_subgraph(
                    tasks_a_single_step_upstream_of_the_supertask
                )
            )

            intersecting_upper_tasks_in_upstream_hierarchy = (
                tasks_a_single_step_upstream_of_the_supertask_superior_subgraph.tasks()
                & dependee_tasks_of_either_subtask_or_its_inferior_tasks
            )

            intersecting_upper_tasks_in_upstream_hierarchy_and_their_inferior_tasks = (
                itertools.chain(
                    intersecting_upper_tasks_in_upstream_hierarchy,
                    self._hierarchy_graph.inferior_tasks(
                        intersecting_upper_tasks_in_upstream_hierarchy
                    ),
                )
            )

            intersecting_lower_tasks_in_upstream_hierarchy = set(
                filter(
                    lambda task: task in tasks_a_single_step_upstream_of_the_supertask,
                    intersecting_upper_tasks_in_upstream_hierarchy_and_their_inferior_tasks,
                )
            )

            cross_hierarchy_dependencies = list[tuple[UID, UID]]()

            intersecting_upper_tasks_in_new_hierarchy = list[UID]()
            for supertask_or_its_superior_task in supertask_and_its_superior_tasks:
                dependee_tasks_in_upstream_hierarchy = (
                    self._dependency_graph.dependee_tasks(
                        supertask_or_its_superior_task
                    )
                    & intersecting_lower_tasks_in_upstream_hierarchy
                )
                if not dependee_tasks_in_upstream_hierarchy:
                    continue
                intersecting_upper_tasks_in_new_hierarchy.append(
                    supertask_or_its_superior_task
                )
                for dependee_task in dependee_tasks_in_upstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (dependee_task, supertask_or_its_superior_task)
                    )

            intersecting_lower_tasks_in_new_hierarchy = list[UID]()
            for subtask_or_its_inferior_task in subtask_and_its_inferior_tasks:
                dependee_tasks_in_upstream_hierarchy = (
                    self._dependency_graph.dependee_tasks(subtask_or_its_inferior_task)
                    & intersecting_upper_tasks_in_upstream_hierarchy
                )
                if not dependee_tasks_in_upstream_hierarchy:
                    continue
                intersecting_lower_tasks_in_new_hierarchy.append(
                    subtask_or_its_inferior_task
                )
                for dependee_task in dependee_tasks_in_upstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (dependee_task, subtask_or_its_inferior_task)
                    )

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_new_hierarchy, [supertask]
            )
            builder.add_hierarchy_connecting_subgraph(
                [subtask], intersecting_lower_tasks_in_new_hierarchy
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_upstream_hierarchy,
                intersecting_lower_tasks_in_upstream_hierarchy,
            )
            for dependee_task, dependent_task in cross_hierarchy_dependencies:
                builder.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyCrossoverError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_crossover_with_downstream_hierarchy(
            self, supertask=supertask, subtask=subtask
        ):
            supertask_and_its_superior_tasks = set(
                itertools.chain(
                    [supertask], self._hierarchy_graph.superior_tasks([supertask])
                )
            )
            tasks_a_single_step_downstream_of_the_supertask = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        supertask_and_its_superior_tasks,
                    )
                )
            )

            subtask_and_its_inferior_tasks = set(
                itertools.chain(
                    [subtask], self._hierarchy_graph.inferior_tasks([subtask])
                )
            )

            dependent_tasks_of_either_subtask_or_its_inferior_tasks = set(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        subtask_and_its_inferior_tasks,
                    )
                )
            )

            tasks_a_single_step_downstream_of_the_supertask_superior_subgraph = (
                self._hierarchy_graph.superior_subgraph(
                    tasks_a_single_step_downstream_of_the_supertask
                )
            )

            intersecting_upper_tasks_in_downstream_hierarchy = (
                tasks_a_single_step_downstream_of_the_supertask_superior_subgraph.tasks()
                & dependent_tasks_of_either_subtask_or_its_inferior_tasks
            )

            intersecting_upper_tasks_in_downstream_hierarchy_and_their_inferior_tasks = itertools.chain(
                intersecting_upper_tasks_in_downstream_hierarchy,
                self._hierarchy_graph.inferior_tasks(
                    intersecting_upper_tasks_in_downstream_hierarchy
                ),
            )

            intersecting_lower_tasks_in_downstream_hierarchy = set(
                filter(
                    lambda task: task
                    in tasks_a_single_step_downstream_of_the_supertask,
                    intersecting_upper_tasks_in_downstream_hierarchy_and_their_inferior_tasks,
                )
            )

            cross_hierarchy_dependencies = list[tuple[UID, UID]]()

            intersecting_upper_tasks_in_new_hierarchy = list[UID]()
            for supertask_or_its_superior_task in supertask_and_its_superior_tasks:
                dependent_tasks_in_downstream_hierarchy = (
                    self._dependency_graph.dependent_tasks(
                        supertask_or_its_superior_task
                    )
                    & intersecting_lower_tasks_in_downstream_hierarchy
                )
                if not dependent_tasks_in_downstream_hierarchy:
                    continue
                intersecting_upper_tasks_in_new_hierarchy.append(
                    supertask_or_its_superior_task
                )
                for dependent_task in dependent_tasks_in_downstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (supertask_or_its_superior_task, dependent_task)
                    )

            intersecting_lower_tasks_in_new_hierarchy = list[UID]()
            for subtask_or_its_inferior_task in subtask_and_its_inferior_tasks:
                dependent_tasks_in_downstream_hierarchy = (
                    self._dependency_graph.dependent_tasks(subtask_or_its_inferior_task)
                    & intersecting_upper_tasks_in_downstream_hierarchy
                )
                if not dependent_tasks_in_downstream_hierarchy:
                    continue
                intersecting_lower_tasks_in_new_hierarchy.append(
                    subtask_or_its_inferior_task
                )
                for dependent_task in dependent_tasks_in_downstream_hierarchy:
                    cross_hierarchy_dependencies.append(
                        (subtask_or_its_inferior_task, dependent_task)
                    )

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_new_hierarchy, [supertask]
            )
            builder.add_hierarchy_connecting_subgraph(
                [subtask], intersecting_lower_tasks_in_new_hierarchy
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_upper_tasks_in_downstream_hierarchy,
                intersecting_lower_tasks_in_downstream_hierarchy,
            )
            for dependee_task, dependent_task in cross_hierarchy_dependencies:
                builder.add_dependency(dependee_task, dependent_task)

            raise HierarchyIntroducesDependencyCrossoverError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=builder.build(),
            )

    @override
    def validate_dependency_can_be_added(
        self, dependee_task: UID, dependent_task: UID, /
    ) -> None:
        """Validate that dependency can be added to the graph."""

        def has_dependency_duplication_with_superior_tasks(
            dependee_task: UID, dependent_task: UID
        ) -> bool:
            """Check if there are duplicate dependencies in the superior tasks.

            Aka: Check if any of the tasks superior-or-equal to the dependee task are
            dependees of any of the tasks superior-or-equal to the dependent task.
            """
            dependee_task_and_its_superior_tasks = itertools.chain(
                [dependee_task], self._hierarchy_graph.superior_tasks([dependee_task])
            )
            tasks_one_step_downstream_of_the_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        dependee_task_and_its_superior_tasks,
                    )
                )
            )
            dependent_task_and_its_superior_tasks = LazyContainer(
                itertools.chain(
                    [dependent_task],
                    self._hierarchy_graph.superior_tasks([dependent_task]),
                )
            )

            return any(
                task in dependent_task_and_its_superior_tasks
                for task in tasks_one_step_downstream_of_the_dependee_task
            )

        def has_dependency_duplication_with_inferior_tasks(
            dependee_task: UID, dependent_task: UID
        ) -> bool:
            """Check if there are duplicate dependencies in the inferior tasks.

            Aka: Check if any of the tasks inferior-or-equal to the dependee task are
            dependees of any the tasks inferior-or-equal to the dependent task.
            """
            dependee_task_and_its_inferior_tasks = itertools.chain(
                [dependee_task], self._hierarchy_graph.inferior_tasks([dependee_task])
            )
            dependent_tasks_of_dependee_task_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        dependee_task_and_its_inferior_tasks,
                    )
                )
            )
            dependent_task_and_its_inferior_tasks = LazyContainer(
                itertools.chain(
                    [dependent_task],
                    self._hierarchy_graph.inferior_tasks([dependent_task]),
                )
            )

            return any(
                task in dependent_task_and_its_inferior_tasks
                for task in dependent_tasks_of_dependee_task_and_its_inferior_tasks
            )

        def has_dependency_crossover_with_dependee_superior_tasks_and_dependent_inferior_tasks(
            dependee_task: UID, dependent_task: UID
        ) -> bool:
            """Check if there is dependency crossover between dependee superior tasks and dependent inferior tasks.

            Aka: Check if any of the tasks superior to the dependee task are
            dependees of any of the tasks inferior to the dependent task.
            """
            tasks_one_step_downstream_of_the_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        self._hierarchy_graph.superior_tasks([dependee_task]),
                    )
                )
            )
            inferior_tasks_of_dependent_task = LazyContainer(
                self._hierarchy_graph.inferior_tasks([dependent_task])
            )

            return any(
                task in inferior_tasks_of_dependent_task
                for task in tasks_one_step_downstream_of_the_dependee_task
            )

        def has_dependency_crossover_with_dependee_inferior_tasks_and_dependent_superior_tasks(
            dependee_task: UID, dependent_task: UID
        ) -> bool:
            """Check if there is dependency crossover between dependee inferior tasks and dependent superior tasks.

            Aka: Check if any of the tasks inferior to the dependee task are dependees
            of any of the tasks superior to the dependent task.
            """
            dependent_tasks_of_inferior_tasks_of_the_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        self._hierarchy_graph.inferior_tasks([dependee_task]),
                    )
                )
            )
            superior_tasks_of_dependent_task = LazyContainer(
                self._hierarchy_graph.superior_tasks([dependent_task])
            )

            return any(
                task in superior_tasks_of_dependent_task
                for task in dependent_tasks_of_inferior_tasks_of_the_dependee_task
            )

        self._dependency_graph.validate_dependency_can_be_added(
            dependee_task, dependent_task
        )

        try:
            super().validate_dependency_can_be_added(dependee_task, dependent_task)
        except DependencyIntroducesUnconstrainedNetworkCycleError as e:
            hierarchy_graph = HierarchyGraph(
                (task, e.connecting_subgraph.hierarchy_graph().subtasks(task))
                for task in e.connecting_subgraph.hierarchy_graph().tasks()
            )
            dependency_graph = DependencyGraph(
                (task, e.connecting_subgraph.dependency_graph().dependent_tasks(task))
                for task in e.connecting_subgraph.dependency_graph().tasks()
            )
            connecting_subgraph = NetworkGraph(
                dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
            )
            raise DependencyIntroducesNetworkCycleError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=connecting_subgraph,
            ) from None

        if has_dependency_duplication_with_superior_tasks(
            dependee_task=dependee_task, dependent_task=dependent_task
        ):
            dependee_task_and_its_superior_tasks = {
                dependee_task,
                *self._hierarchy_graph.superior_tasks([dependee_task]),
            }

            tasks_one_step_downstream_of_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        dependee_task_and_its_superior_tasks,
                    )
                )
            )

            dependent_task_and_its_superior_tasks = LazyContainer(
                itertools.chain(
                    [dependent_task],
                    self._hierarchy_graph.superior_tasks([dependent_task]),
                )
            )

            intersecting_dependent_task_and_its_superior_tasks = set(
                filter(
                    lambda task: task in dependent_task_and_its_superior_tasks,
                    tasks_one_step_downstream_of_dependee_task,
                )
            )

            intersecting_dependencies_map = collections.defaultdict[UID, set[UID]](set)
            for (
                intersecting_dependent_task_or_its_superior_task
            ) in intersecting_dependent_task_and_its_superior_tasks:
                for (
                    dependee_task_of_intersecting_dependent_task_or_its_superior_task
                ) in self._dependency_graph.dependee_tasks(
                    intersecting_dependent_task_or_its_superior_task
                ):
                    if (
                        dependee_task_of_intersecting_dependent_task_or_its_superior_task
                        not in dependee_task_and_its_superior_tasks
                    ):
                        continue
                    intersecting_dependencies_map[
                        dependee_task_of_intersecting_dependent_task_or_its_superior_task
                    ].add(intersecting_dependent_task_or_its_superior_task)

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_dependencies_map.keys(),
                [dependee_task],
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_dependent_task_and_its_superior_tasks, [dependent_task]
            )
            for (
                intersecting_dependee_task,
                intersecting_dependent_tasks,
            ) in intersecting_dependencies_map.items():
                for intersecting_dependent_task in intersecting_dependent_tasks:
                    builder.add_dependency(
                        intersecting_dependee_task, intersecting_dependent_task
                    )

            raise DependencyIntroducesDependencyDuplicationError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_duplication_with_inferior_tasks(
            dependee_task=dependee_task, dependent_task=dependent_task
        ):
            dependee_task_and_its_inferior_tasks = {
                dependee_task,
                *self._hierarchy_graph.inferior_tasks([dependee_task]),
            }

            dependent_tasks_of_dependee_task_and_its_inferior_tasks = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        dependee_task_and_its_inferior_tasks,
                    )
                )
            )

            dependent_task_and_its_inferior_tasks = LazyContainer(
                itertools.chain(
                    [dependent_task],
                    self._hierarchy_graph.inferior_tasks([dependent_task]),
                )
            )

            intersecting_dependent_task_and_its_inferior_tasks = set(
                filter(
                    lambda task: task in dependent_task_and_its_inferior_tasks,
                    dependent_tasks_of_dependee_task_and_its_inferior_tasks,
                )
            )

            intersecting_dependencies_map = collections.defaultdict[UID, set[UID]](set)
            for (
                intersecting_dependent_task_or_its_inferior_task
            ) in intersecting_dependent_task_and_its_inferior_tasks:
                for (
                    dependee_task_of_intersecting_dependent_task_or_its_inferior_task
                ) in self._dependency_graph.dependee_tasks(
                    intersecting_dependent_task_or_its_inferior_task
                ):
                    if (
                        dependee_task_of_intersecting_dependent_task_or_its_inferior_task
                        not in dependee_task_and_its_inferior_tasks
                    ):
                        continue
                    intersecting_dependencies_map[
                        dependee_task_of_intersecting_dependent_task_or_its_inferior_task
                    ].add(intersecting_dependent_task_or_its_inferior_task)

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                [dependee_task],
                intersecting_dependencies_map.keys(),
            )
            builder.add_hierarchy_connecting_subgraph(
                [dependent_task], intersecting_dependent_task_and_its_inferior_tasks
            )
            for (
                intersecting_dependee_task,
                intersecting_dependent_tasks,
            ) in intersecting_dependencies_map.items():
                for intersecting_dependent_task in intersecting_dependent_tasks:
                    builder.add_dependency(
                        intersecting_dependee_task, intersecting_dependent_task
                    )

            raise DependencyIntroducesDependencyDuplicationError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_crossover_with_dependee_superior_tasks_and_dependent_inferior_tasks(
            dependee_task=dependee_task, dependent_task=dependent_task
        ):
            superior_tasks_of_dependee_task = set(
                self._hierarchy_graph.superior_tasks([dependee_task])
            )

            dependent_tasks_of_superior_tasks_of_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        superior_tasks_of_dependee_task,
                    )
                )
            )

            inferior_tasks_of_dependent_task = LazyContainer(
                self._hierarchy_graph.inferior_tasks([dependent_task])
            )

            intersecting_inferior_tasks_of_dependent_task = set(
                filter(
                    lambda task: task in inferior_tasks_of_dependent_task,
                    dependent_tasks_of_superior_tasks_of_dependee_task,
                )
            )

            intersecting_dependencies_map = collections.defaultdict[UID, set[UID]](set)
            for (
                intersecting_inferior_task_of_dependent_task
            ) in intersecting_inferior_tasks_of_dependent_task:
                for (
                    dependee_task_of_intersecting_inferior_task_of_dependent_task
                ) in self._dependency_graph.dependee_tasks(
                    intersecting_inferior_task_of_dependent_task
                ):
                    if (
                        dependee_task_of_intersecting_inferior_task_of_dependent_task
                        not in superior_tasks_of_dependee_task
                    ):
                        continue
                    intersecting_dependencies_map[
                        dependee_task_of_intersecting_inferior_task_of_dependent_task
                    ].add(intersecting_inferior_task_of_dependent_task)

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                intersecting_dependencies_map.keys(),
                [dependee_task],
            )
            builder.add_hierarchy_connecting_subgraph(
                [dependent_task], intersecting_inferior_tasks_of_dependent_task
            )
            for (
                intersecting_dependee_task,
                intersecting_dependent_tasks,
            ) in intersecting_dependencies_map.items():
                for intersecting_dependent_task in intersecting_dependent_tasks:
                    builder.add_dependency(
                        intersecting_dependee_task, intersecting_dependent_task
                    )
            raise DependencyIntroducesDependencyCrossoverError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

        if has_dependency_crossover_with_dependee_inferior_tasks_and_dependent_superior_tasks(
            dependee_task=dependee_task, dependent_task=dependent_task
        ):
            inferior_tasks_of_dependee_task = set(
                self._hierarchy_graph.inferior_tasks([dependee_task])
            )

            dependent_tasks_of_inferior_tasks_of_dependee_task = unique(
                itertools.chain.from_iterable(
                    map(
                        self._dependency_graph.dependent_tasks,
                        inferior_tasks_of_dependee_task,
                    )
                )
            )

            superior_tasks_of_dependent_task = LazyContainer(
                self._hierarchy_graph.superior_tasks([dependent_task])
            )

            intersecting_superior_tasks_of_dependent_task = set(
                filter(
                    lambda task: task in superior_tasks_of_dependent_task,
                    dependent_tasks_of_inferior_tasks_of_dependee_task,
                )
            )

            intersecting_dependencies_map = collections.defaultdict[UID, set[UID]](set)
            for (
                intersecting_superior_task_of_dependent_task
            ) in intersecting_superior_tasks_of_dependent_task:
                for (
                    dependee_task_of_intersecting_superior_task_of_dependent_task
                ) in self._dependency_graph.dependee_tasks(
                    intersecting_superior_task_of_dependent_task
                ):
                    if (
                        dependee_task_of_intersecting_superior_task_of_dependent_task
                        not in inferior_tasks_of_dependee_task
                    ):
                        continue
                    intersecting_dependencies_map[
                        dependee_task_of_intersecting_superior_task_of_dependent_task
                    ].add(intersecting_superior_task_of_dependent_task)

            builder = NetworkSubgraphBuilder(self)
            builder.add_hierarchy_connecting_subgraph(
                [dependee_task], intersecting_dependencies_map.keys()
            )
            builder.add_hierarchy_connecting_subgraph(
                intersecting_superior_tasks_of_dependent_task, [dependent_task]
            )
            for (
                intersecting_dependee_task,
                intersecting_dependent_tasks,
            ) in intersecting_dependencies_map.items():
                for intersecting_dependent_task in intersecting_dependent_tasks:
                    builder.add_dependency(
                        intersecting_dependee_task, intersecting_dependent_task
                    )
            raise DependencyIntroducesDependencyCrossoverError(
                dependee_task=dependee_task,
                dependent_task=dependent_task,
                connecting_subgraph=builder.build(),
            )

    @override
    def downstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
        """Return subgraph of all tasks downstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't downstream
        of any of the tasks, but are required to connect all downstream tasks
        correctly. I'm calling these non-downstream tasks.
        """
        builder = NetworkSubgraphBuilder(self)
        builder.add_downstream_subgraph(tasks)
        return builder.build()

    @override
    def upstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
        """Return subgraph of all tasks upstream of at least one of the tasks.

        Note that the subgraph will contain a few tasks that aren't upstream
        of any of the tasks, but are required to connect all upstream tasks
        correctly. I'm calling these non-upstream tasks and are returned along
        with the subgraph.
        """
        builder = NetworkSubgraphBuilder(self)
        builder.add_upstream_subgraph(tasks)
        return builder.build()

    @override
    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> NetworkGraph:
        """Return subgraph of tasks between the source tasks and target tasks.

        All target tasks must be downstream of at least one of the source tasks.
        """
        builder = NetworkSubgraphBuilder(self)
        builder.add_connecting_subgraph(source_tasks, target_tasks)
        return builder.build()

    @override
    def component_subgraph(self, task: UID, /) -> NetworkGraph:
        """Return subgraph of all tasks in the same connected component as task."""
        builder = NetworkSubgraphBuilder(self)
        builder.add_component_subgraph(task)
        return builder.build()

    @override
    def component_subgraphs(self) -> Generator[NetworkGraph, None, None]:
        """Return generator of connected components."""
        checked_tasks = set[UID]()
        for node in self.tasks():
            if node in checked_tasks:
                continue

            component = self.component_subgraph(node)
            checked_tasks.update(component.tasks())
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

    def clone(self) -> NetworkGraph:
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

    def downstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
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

    def upstream_subgraph(self, tasks: Iterable[UID], /) -> NetworkGraph:
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
    ) -> NetworkGraph:
        """Return subgraph of tasks between the source tasks and target tasks.

        All target tasks must be downstream of at least one of the source tasks.
        """
        return self._graph.connecting_subgraph(source_tasks, target_tasks)

    def component_subgraph(self, task: UID, /) -> NetworkGraph:
        """Return subgraph of all tasks in the same connected component as task."""
        return self._graph.component_subgraph(task)

    def component_subgraphs(self) -> Generator[NetworkGraph, None, None]:
        """Return generator of connected components."""
        return self._graph.component_subgraphs()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependencies, dependents, subtasks or supertasks."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._graph.isolated_tasks()
