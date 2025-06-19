"""Hierarchy Graph and associated classes/exceptions."""

from __future__ import annotations

import functools
from collections.abc import Callable, Generator, Iterable, Iterator, Set
from typing import Any, ParamSpec, Protocol, TypeVar

from graft import graphs
from graft.domain.tasks import helpers
from graft.domain.tasks.helpers import (
    TaskDoesNotExistError,
    reraise_node_already_exists_as_task_already_exists,
)
from graft.domain.tasks.uid import (
    UID,
    SubgraphTasksView,
    TasksView,
)


class HasSuperTasksError(Exception):
    """Raised when a task has super-tasks."""

    def __init__(
        self,
        task: UID,
        supertasks: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HasSuperTasksError."""
        self.task = task
        self.supertasks = set(supertasks)
        formatted_supertasks = (str(supertask) for supertask in supertasks)
        super().__init__(
            f"Task [{task}] has super-tasks [{", ".join(formatted_supertasks)}]",
            *args,
            **kwargs,
        )


class HasSubTasksError(Exception):
    """Raised when a task has sub-tasks."""

    def __init__(
        self,
        task: UID,
        subtasks: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HasSubTasksError."""
        self.task = task
        self.subtasks = set(subtasks)
        formatted_subtasks = (str(task) for task in subtasks)
        super().__init__(
            f"Task [{task}] has sub-tasks [{", ".join(formatted_subtasks)}]",
            *args,
            **kwargs,
        )


class HierarchyAlreadyExistsError(Exception):
    """Raised when a hierarchy between specified tasks already exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HierarchyAlreadyExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Hierarchy between supertask [{supertask}] and subtask [{subtask}] already exists",
            *args,
            **kwargs,
        )


class HierarchyDoesNotExistError(Exception):
    """Raised when a hierarchy between tasks does not exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HierarchyDoesNotExistError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Hierarchy between supertask [{supertask}] and subtask [{subtask}] does not exist",
            *args,
            **kwargs,
        )


class HierarchyLoopError(Exception):
    """Loop error.

    Raised when a hierarchy is referenced that connects a task to itself, creating a
    loop. These aren't allowed in simple digraphs.
    """

    def __init__(
        self,
        task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize LoopError."""
        self.task = task
        super().__init__(f"Hierarchy loop [{task}]", *args, **kwargs)


class NoConnectingHierarchySubgraphError(Exception):
    """Raised when no connecting subgraph exists."""

    def __init__(
        self,
        sources: Iterable[UID],
        targets: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NoConnectingHierarchySubgraphError."""
        self.sources = list(sources)
        self.targets = list(targets)

        formatted_sources = ", ".join(str(source) for source in sources)
        formatted_targets = ", ".join(str(target) for target in targets)
        super().__init__(
            f"no connecting subgraph from tasks [{formatted_sources}] to tasks [{formatted_targets}] exists",
            *args,
            **kwargs,
        )


class HierarchyIntroducesCycleError(Exception):
    """Adding the hierarchy introduces a cycle to the graph."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: HierarchyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize HierarchyIntroducesCycleError."""
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"hierarchy between supertask [{supertask}] and subtask [{subtask}] introduces cycle",
            *args,
            **kwargs,
        )


class HierarchyIntroducesRedundantHierarchyError(Exception):
    """Adding the hierarchy introduces a redundant hierarchy to the graph."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: HierarchyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize HierarchyIntroducesRedundantHierarchyError."""
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"hierarchy between supertask [{supertask}] and subtask [{subtask}] is redundant",
            *args,
            **kwargs,
        )


P = ParamSpec("P")
R = TypeVar("R")


def _reraise_edge_adding_exceptions_as_corresponding_hierarchy_adding_exceptions(
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_edge_can_be_added exceptions as their corresponding validate_hierarchy_can_be_added exceptions."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except graphs.NodeDoesNotExistError as e:
            assert isinstance(e.node, UID)
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            assert isinstance(e.node, UID)
            raise HierarchyLoopError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            assert isinstance(e.source, UID)
            assert isinstance(e.target, UID)
            raise HierarchyAlreadyExistsError(e.source, e.target) from e
        except graphs.IntroducesCycleError as e:
            assert isinstance(e.source, UID)
            assert isinstance(e.target, UID)
            assert all(isinstance(node, UID) for node in e.connecting_subgraph.nodes())
            connecting_subgraph = graphs.ReducedDirectedAcyclicGraph[UID]()
            connecting_subgraph.update(e.connecting_subgraph)
            raise HierarchyIntroducesCycleError(
                supertask=e.source,
                subtask=e.target,
                connecting_subgraph=HierarchyGraph(connecting_subgraph),
            ) from e
        except graphs.IntroducesRedundantEdgeError as e:
            assert isinstance(e.source, UID)
            assert isinstance(e.target, UID)
            assert all(isinstance(node, UID) for node in e.subgraph.nodes())
            raise HierarchyIntroducesRedundantHierarchyError(
                supertask=e.source,
                subtask=e.target,
                connecting_subgraph=HierarchyGraph(e.subgraph),
            ) from e

    return wrapper


def _reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions(
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_node_can_be_removed exceptions as their corresponding validate_task_can_be_removed exceptions."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except graphs.NodeDoesNotExistError as e:
            assert isinstance(e.node, UID)
            raise TaskDoesNotExistError(e.node) from e
        except graphs.HasPredecessorsError as e:
            assert isinstance(e.node, UID)
            raise HasSuperTasksError(task=e.node, supertasks=e.predecessors) from e
        except graphs.HasSuccessorsError as e:
            assert isinstance(e.node, UID)
            raise HasSubTasksError(task=e.node, subtasks=e.successors) from e

    return wrapper


class HierarchiesView(Set[tuple[UID, UID]]):
    """View of the hierarchies in the graph."""

    def __init__(self, heirarchies: Set[tuple[UID, UID]], /) -> None:
        """Initialise HierarchiesView."""
        self._hierarchies = heirarchies

    def __bool__(self) -> bool:
        """Check if view has any hierarchies."""
        return bool(self._hierarchies)

    def __len__(self) -> int:
        """Return number of hierarchies."""
        return len(self._hierarchies)

    def __contains__(self, item: object) -> bool:
        """Check if item in HierarchiesView."""
        # TODO: Doesn't make sense to catch this error for generic self._heirarchies
        try:
            return item in self._hierarchies
        except graphs.NodeDoesNotExistError as e:
            assert isinstance(e.node, UID)
            raise TaskDoesNotExistError(e.node) from e

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return generator over hierarchies in view."""
        return iter(self._hierarchies)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return isinstance(other, HierarchiesView) and set(self) == set(other)

    def __str__(self) -> str:
        """Return string representation of hierarchies."""
        task_subtask_pairs = (f"({task}, {subtask})" for task, subtask in self)
        return f"{{{', '.join(task_subtask_pairs)}}}"

    def __repr__(self) -> str:
        """Return string representation of hierarchies."""
        task_subtask_pairs = (f"({task!r}, {subtask!r})" for task, subtask in self)
        return f"{self.__class__.__name__}({{{', '.join(task_subtask_pairs)}}})"

    def __sub__(self, other: Set[Any]) -> HierarchiesView:
        """Return difference of two views."""
        return HierarchiesView(self._hierarchies - other)

    def __and__(self, other: Set[Any]) -> HierarchiesView:
        """Return intersection of two views."""
        return HierarchiesView(self._hierarchies & other)

    def __or__(self, other: Set[tuple[UID, UID]]) -> HierarchiesView:
        """Return union of two views."""
        return HierarchiesView(self._hierarchies | other)

    def __xor__(self, other: Set[tuple[UID, UID]]) -> HierarchiesView:
        """Return symmetric difference of two views."""
        return HierarchiesView(self._hierarchies ^ other)


class HierarchySubgraphHierarchyView(Set[tuple[UID, UID]]):
    """View of subgraph hierarchies."""

    def __init__(self, hierarchies: graphs.SubgraphEdgesView[UID], /) -> None:
        """Initialise HierarchySubgraphHierarchyView."""
        self._hierarchies = hierarchies

    def __bool__(self) -> bool:
        """Check if view has any hierarchies."""
        return bool(self._hierarchies)

    def __eq__(self, other: object) -> bool:
        """Check if subgraph hierarchies view is equal to other."""
        return isinstance(other, HierarchySubgraphHierarchyView) and set(self) == set(
            other
        )

    def __contains__(self, item: object) -> bool:
        """Check if item is a hierarchy in the subgraph."""
        return item in self._hierarchies

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return iterator over hierarchies in view."""
        return iter(self._hierarchies)

    def __len__(self) -> int:
        """Return number of hierarchies in view."""
        return len(self._hierarchies)

    def contains(
        self, tasks_: Iterable[tuple[UID, UID]]
    ) -> Generator[bool, None, None]:
        """Check if hierarchies are in the subgraph.

        Theoretically faster than checking if the subgraph contains multiple
        hierarchies one at a time, as can cache the parts of the subgraph
        already searched.
        """
        return self._hierarchies.contains(edges=tasks_)


class MultipleStartingTasksHierarchySubgraphView:
    """View of a hierarchy subgraph with multiple starting tasks."""

    def __init__(
        self,
        subgraph: graphs.MultipleStartingNodesReducedDirectedAcyclicSubgraphView[UID],
    ) -> None:
        """Initialise SubgraphView."""
        self._subgraph = subgraph

    def __bool__(self) -> bool:
        """Check if subgraph is not empty."""
        return bool(self._subgraph)

    def __eq__(self, other: object) -> bool:
        """Check if hierarchy subgraph view is equal to other."""
        return (
            isinstance(other, MultipleStartingTasksHierarchySubgraphView)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def tasks(self) -> SubgraphTasksView:
        """Return view of tasks in subgraph."""
        return SubgraphTasksView(self._subgraph.nodes())

    def hierarchies(self) -> HierarchySubgraphHierarchyView:
        """Return view of dependencies in subgraph."""
        return HierarchySubgraphHierarchyView(self._subgraph.edges())

    def subgraph(self) -> HierarchyGraph:
        """Create a concrete copy of the subgraph."""
        return HierarchyGraph(self._subgraph.subgraph())


class SingleStartingTaskHierarchySubgraphView(
    MultipleStartingTasksHierarchySubgraphView
):
    """View of a hierarchy subgraph with a single starting task."""

    def __init__(
        self, subgraph: graphs.SingleStartingNodeDirectedAcyclicSubgraphView[UID]
    ) -> None:
        """Initialise SubgraphView."""
        self._subgraph = subgraph

    def traverse(
        self, order: graphs.TraversalOrder = graphs.TraversalOrder.BREADTH_FIRST
    ) -> Generator[UID, None, None]:
        """Return generator over tasks in subgraph in order.

        Starts from the starting node, but does not include it.
        """
        return iter(self._subgraph.traverse(order=order))


class IHierarchyGraphView(Protocol):
    """Interface for a view of a graph of task hierarchies."""

    def __bool__(self) -> bool:
        """Check if graph has any tasks."""
        ...

    def __str__(self) -> str:
        """Return string representation of graph."""
        ...

    def __repr__(self) -> str:
        """Return string representation of graph."""
        ...

    def tasks(self) -> TasksView:
        """Return view of tasks in graph."""
        ...

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        ...

    def supertasks(self, task: UID, /) -> TasksView:
        """Return view of supertasks of task."""
        ...

    def subtasks(self, task: UID, /) -> TasksView:
        """Return view of subtasks of task."""
        ...

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView: ...

    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView: ...

    def inferior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView: ...

    def superior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView: ...

    def has_path(
        self,
        source_task: UID,
        target_task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> bool:
        """Check if there is a path from source to target tasks.

        Stop searching beyond a specific task if the stop condition is met.
        """
        ...

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between the source and target task."""
        ...

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        ...

    def task_subtasks_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
        """Return generator over task-subtasks pairs."""
        ...

    def is_concrete(self, task: UID, /) -> bool:
        """Check if task is concrete.

        Concrete tasks have no sub-tasks.
        """
        ...

    def concrete_tasks(self) -> Generator[UID, None, None]:
        """Return generator over concrete tasks."""
        ...

    def is_top_level(self, task: UID, /) -> bool:
        """Check if task is top-level.

        Top-level tasks have no super-tasks.
        """
        ...

    def top_level_tasks(self) -> Generator[UID, None, None]:
        """Return generator over top-level tasks."""
        ...

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no super-tasks nor sub-tasks."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator over isolated tasks."""
        ...


class HierarchyGraph:
    """Graph of task hierarchies.

    Shows which tasks are subtasks of other tasks.

    Acts as a Minimum DAG.
    """

    @classmethod
    def clone(cls, graph: IHierarchyGraphView, /) -> HierarchyGraph:
        """Create a clone of a hierarchy graph from an interface."""
        clone = cls()
        clone.update(graph)
        return clone

    def __init__(
        self, reduced_dag: graphs.ReducedDirectedAcyclicGraph[UID] | None = None
    ) -> None:
        """Initialise HierarchyGraph."""
        self._reduced_dag = reduced_dag or graphs.ReducedDirectedAcyclicGraph[UID]()

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._reduced_dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        return (
            isinstance(other, HierarchyGraph)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        return str(self._reduced_dag)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = (
            f"{task!r}: {{{", ".join(repr(subtask) for subtask in subtasks)}}}"
            for task, subtasks in self.task_subtasks_pairs()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_subtasks)}}})"

    def tasks(self) -> TasksView:
        """Return view of tasks in graph."""
        return TasksView(self._reduced_dag.nodes())

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        return HierarchiesView(self._reduced_dag.edges())

    def supertasks(self, task: UID, /) -> TasksView:
        """Return view of supertasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            supertasks = self._reduced_dag.predecessors(task)
        return TasksView(supertasks)

    def subtasks(self, task: UID, /) -> TasksView:
        """Return view of subtasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            subtasks = self._reduced_dag.successors(task)
        return TasksView(subtasks)

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            descendants = self._reduced_dag.descendants(
                task, stop_condition=stop_condition
            )
        return SingleStartingTaskHierarchySubgraphView(descendants)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            ancestors = self._reduced_dag.ancestors(task, stop_condition=stop_condition)
        return SingleStartingTaskHierarchySubgraphView(ancestors)

    def inferior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            inferior_tasks = self._reduced_dag.descendants_multi(
                tasks, stop_condition=stop_condition
            )
        return MultipleStartingTasksHierarchySubgraphView(subgraph=inferior_tasks)

    def superior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            superior_tasks = self._reduced_dag.ancestors_multi(
                tasks, stop_condition=stop_condition
            )
        return MultipleStartingTasksHierarchySubgraphView(subgraph=superior_tasks)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def has_path(
        self,
        source_task: UID,
        target_task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> bool:
        """Check if there is a path from source to target tasks.

        Stop searching beyond a specific task if the stop condition is met.
        """
        return self._reduced_dag.has_path(
            source=source_task, target=target_task, stop_condition=stop_condition
        )

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        try:
            connecting_subgraph = self._reduced_dag.connecting_subgraph_multi(
                sources=source_tasks, targets=target_tasks
            )
        except graphs.NodeDoesNotExistError as e:
            assert isinstance(e.node, UID)
            raise TaskDoesNotExistError(task=e.node) from e
        except graphs.NoConnectingSubgraphError as e:
            assert all(isinstance(source, UID) for source in e.sources)
            assert all(isinstance(target, UID) for target in e.targets)
            raise NoConnectingHierarchySubgraphError(
                sources=e.sources, targets=e.targets
            ) from e

        return HierarchyGraph(reduced_dag=connecting_subgraph)

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between the source and target task."""
        return self.connecting_subgraph_multi([source_task], [target_task])

    @reraise_node_already_exists_as_task_already_exists()
    def add_task(self, task: UID, /) -> None:
        """Add a task to the graph."""
        self._reduced_dag.add_node(task)

    @_reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions
    def validate_task_can_be_removed(self, task: UID, /) -> None:
        """Validate that task can be removed from the graph."""
        self._reduced_dag.validate_node_can_be_removed(task)

    @_reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions
    def remove_task(self, task: UID, /) -> None:
        """Remove a task."""
        self._reduced_dag.remove_node(task)

    @_reraise_edge_adding_exceptions_as_corresponding_hierarchy_adding_exceptions
    def validate_hierarchy_can_be_added(self, supertask: UID, subtask: UID, /) -> None:
        """Validate that hierarchy can be added to the graph."""
        self._reduced_dag.validate_edge_can_be_added(source=supertask, target=subtask)

    @_reraise_edge_adding_exceptions_as_corresponding_hierarchy_adding_exceptions
    def add_hierarchy(self, supertask: UID, subtask: UID, /) -> None:
        """Add a hierarchy between the specified tasks."""
        self._reduced_dag.add_edge(source=supertask, target=subtask)

    def remove_hierarchy(self, supertask: UID, subtask: UID, /) -> None:
        """Remove the hierarchy between the specified tasks."""
        try:
            self._reduced_dag.remove_edge(source=supertask, target=subtask)
        except graphs.NodeDoesNotExistError as e:
            assert isinstance(e.node, UID)
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            assert isinstance(e.node, UID)
            raise HierarchyLoopError(supertask) from e
        except graphs.EdgeDoesNotExistError as e:
            assert isinstance(e.source, UID)
            assert isinstance(e.target, UID)
            raise HierarchyDoesNotExistError(supertask, subtask) from e

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_concrete(self, task: UID, /) -> bool:
        """Check if task is concrete.

        Concrete tasks have no sub-tasks.
        """
        return self._reduced_dag.is_leaf(task)

    def concrete_tasks(self) -> Generator[UID, None, None]:
        """Return generator over concrete tasks."""
        return self._reduced_dag.leaves()

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_top_level(self, task: UID, /) -> bool:
        """Check if task is top-level.

        Top-level tasks have no super-tasks.
        """
        return self._reduced_dag.is_root(task)

    def top_level_tasks(self) -> Generator[UID, None, None]:
        """Return generator over top-level tasks."""
        return self._reduced_dag.roots()

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no super-tasks nor sub-tasks."""
        return self._reduced_dag.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator over isolated tasks."""
        return self._reduced_dag.isolated_nodes()

    def task_subtasks_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
        """Return generator over task-subtasks pairs."""
        for task, subtasks in self._reduced_dag.node_successors_pairs():
            yield task, TasksView(subtasks)

    def update(self, graph: IHierarchyGraphView, /) -> None:
        """Update the graph with another graph.

        Use this method with EXTREME CAUTION; the order in which tasks and
        hierarchies are added cannot be controlled, so I recommend only using
        it as a helper method when you know it won't fail.
        """
        for task in graph.tasks():
            if task in self.tasks():
                continue
            self.add_task(task)

        for supertask, subtask in graph.hierarchies():
            if (supertask, subtask) in self.hierarchies():
                continue
            self.add_hierarchy(supertask, subtask)


class HierarchyGraphView:
    """View of the HierarchyGraph."""

    def __init__(self, hierarchy_graph: IHierarchyGraphView) -> None:
        """Initialise HierarchyGraphView."""
        self._graph = hierarchy_graph

    def __bool__(self) -> bool:
        """Check if view is not empty."""
        return bool(self._graph)

    def __eq__(self, other: object) -> bool:
        """Check if two hierarchy graph views are equal."""
        return (
            isinstance(other, HierarchyGraphView)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = (
            f"{task}: {{{", ".join(str(subtask) for subtask in subtasks)}}}"
            for task, subtasks in self.task_subtasks_pairs()
        )
        return f"{{{', '.join(tasks_with_subtasks)}}}"

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = (
            f"{task!r}: {{{", ".join(repr(subtask) for subtask in subtasks)}}}"
            for task, subtasks in self.task_subtasks_pairs()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_subtasks)}}})"

    def tasks(self) -> TasksView:
        """Return tasks in view."""
        return self._graph.tasks()

    def hierarchies(self) -> HierarchiesView:
        """Return hierarchies in view."""
        return self._graph.hierarchies()

    def subtasks(self, task: UID) -> TasksView:
        """Return view of subtasks of task."""
        return self._graph.subtasks(task)

    def supertasks(self, task: UID) -> TasksView:
        """Return view of supertasks of task."""
        return self._graph.supertasks(task)

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView:
        return self._graph.inferior_tasks(task, stop_condition=stop_condition)

    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskHierarchySubgraphView:
        return self._graph.superior_tasks(task, stop_condition=stop_condition)

    def inferior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView:
        return self._graph.inferior_tasks_multi(tasks, stop_condition=stop_condition)

    def superior_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksHierarchySubgraphView:
        return self._graph.superior_tasks_multi(tasks, stop_condition=stop_condition)

    def has_path(
        self,
        source_task: UID,
        target_task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> bool:
        """Check if there is a path from source to target tasks.

        Stop searching beyond a specific task if the stop condition is met.
        """
        return self._graph.has_path(source_task, target_task, stop_condition)

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between the source and target task."""
        return self._graph.connecting_subgraph(source_task, target_task)

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph_multi(source_tasks, target_tasks)

    def task_subtasks_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
        """Return generator over task-subtasks pairs."""
        return self._graph.task_subtasks_pairs()

    def is_concrete(self, task: UID, /) -> bool:
        """Check if task is concrete.

        Concrete tasks have no sub-tasks.
        """
        return self._graph.is_concrete(task)

    def concrete_tasks(self) -> Generator[UID, None, None]:
        """Return generator over concrete tasks."""
        return self._graph.concrete_tasks()

    def is_top_level(self, task: UID, /) -> bool:
        """Check if task is top-level.

        Top-level tasks have no super-tasks.
        """
        return self._graph.is_top_level(task)

    def top_level_tasks(self) -> Generator[UID, None, None]:
        """Return generator over top-level tasks."""
        return self._graph.top_level_tasks()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no super-tasks nor sub-tasks."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator over isolated tasks."""
        return self._graph.isolated_tasks()
