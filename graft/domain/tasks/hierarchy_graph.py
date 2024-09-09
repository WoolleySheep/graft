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
    SubgraphUIDsView,
    UIDsView,
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
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            raise HierarchyLoopError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            raise HierarchyAlreadyExistsError(e.source, e.target) from e
        except graphs.IntroducesCycleError as e:
            raise HierarchyIntroducesCycleError(
                supertask=e.source,
                subtask=e.target,
                connecting_subgraph=HierarchyGraph(e.connecting_subgraph),
            ) from e
        except graphs.IntroducesRedundantEdgeError as e:
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
            raise TaskDoesNotExistError(e.node) from e
        except graphs.HasPredecessorsError as e:
            raise HasSuperTasksError(task=e.node, supertasks=e.predecessors) from e
        except graphs.HasSuccessorsError as e:
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


class HierarchySubgraphView:
    """View of a hierarchy subgraph."""

    def __init__(
        self, subgraph: graphs.ReducedDirectedAcyclicSubgraphView[UID]
    ) -> None:
        """Initialise SubgraphView."""
        self._subgraph = subgraph

    def __bool__(self) -> bool:
        """Check if subgraph is not empty."""
        return bool(self._subgraph)

    def __eq__(self, other: object) -> bool:
        """Check if hierarchy subgraph view is equal to other."""
        return (
            isinstance(other, HierarchySubgraphView)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def tasks(self) -> SubgraphUIDsView:
        """Return view of tasks in subgraph."""
        return SubgraphUIDsView(self._subgraph.nodes())

    def hierarchies(self) -> HierarchySubgraphHierarchyView:
        """Return view of dependencies in subgraph."""
        return HierarchySubgraphHierarchyView(self._subgraph.edges())

    def traverse(
        self, order: graphs.TraversalOrder = graphs.TraversalOrder.BREADTH_FIRST
    ) -> Generator[UID, None, None]:
        """Return generator over tasks in subgraph in order.

        Starts from the starting node, but does not include it.
        """
        return iter(self._subgraph.traverse(order=order))

    def subgraph(self, include_starting_task: bool = False) -> HierarchyGraph:
        """Create a concrete copy of the subgraph."""
        return HierarchyGraph(self._subgraph.subgraph(include_starting_task))


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

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        ...

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        ...

    def supertasks(self, task: UID, /) -> UIDsView:
        """Return view of supertasks of task."""
        ...

    def subtasks(self, task: UID, /) -> UIDsView:
        """Return view of subtasks of task."""
        ...

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        ...

    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        ...

    def inferior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of inferior tasks of multiple tasks.

        This effectively OR's together the superior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        ...

    def superior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of superior tasks of multiple tasks.

        This effectively OR's together the inferior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        ...

    def has_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a path from source to target tasks."""
        ...

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        ...

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
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

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        return UIDsView(self._reduced_dag.nodes())

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        return HierarchiesView(self._reduced_dag.edges())

    def supertasks(self, task: UID, /) -> UIDsView:
        """Return view of supertasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            supertasks = self._reduced_dag.predecessors(task)
        return UIDsView(supertasks)

    def subtasks(self, task: UID, /) -> UIDsView:
        """Return view of subtasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            subtasks = self._reduced_dag.successors(task)
        return UIDsView(subtasks)

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            descendants = self._reduced_dag.descendants(
                task, stop_condition=stop_condition
            )
        return HierarchySubgraphView(descendants)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            ancestors = self._reduced_dag.ancestors(task, stop_condition=stop_condition)
        return HierarchySubgraphView(ancestors)

    def inferior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of inferior tasks of multiple tasks.

        This effectively OR's together the superior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            inferior_tasks_subgraph = self._reduced_dag.descendants_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        return HierarchyGraph(reduced_dag=inferior_tasks_subgraph)

    def superior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of superior tasks of multiple tasks.

        This effectively OR's together the inferior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            superior_tasks_subgraph = self._reduced_dag.ancestors_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        return HierarchyGraph(reduced_dag=superior_tasks_subgraph)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def has_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a path from source to target tasks."""
        return self._reduced_dag.has_path(source=source_task, target=target_task)

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        try:
            connecting_subgraph = self._reduced_dag.connecting_subgraph(
                source=source_task, target=target_task
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e
        except graphs.NoConnectingSubgraphError as e:
            raise NoConnectingHierarchySubgraphError(
                sources=[source_task], targets=[target_task]
            ) from e

        return HierarchyGraph(reduced_dag=connecting_subgraph)

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
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            raise HierarchyLoopError(supertask) from e
        except graphs.EdgeDoesNotExistError as e:
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

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-subtasks pairs."""
        for task, subtasks in self._reduced_dag.node_successors_pairs():
            yield task, UIDsView(subtasks)


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

    def tasks(self) -> UIDsView:
        """Return tasks in view."""
        return self._graph.tasks()

    def hierarchies(self) -> HierarchiesView:
        """Return hierarchies in view."""
        return self._graph.hierarchies()

    def subtasks(self, task: UID) -> UIDsView:
        """Return view of subtasks of task."""
        return self._graph.subtasks(task)

    def supertasks(self, task: UID) -> UIDsView:
        """Return view of supertasks of task."""
        return self._graph.supertasks(task)

    def inferior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        return self._graph.inferior_tasks(task, stop_condition=stop_condition)

    def superior_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchySubgraphView:
        """Yield superior tasks of task, following the specified search order."""
        return self._graph.superior_tasks(task, stop_condition=stop_condition)

    def inferior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of inferior tasks of multiple tasks.

        This effectively OR's together the superior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        return self._graph.inferior_tasks_subgraph_multi(
            tasks, stop_condition=stop_condition
        )

    def superior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        """Return subgraph of superior tasks of multiple tasks.

        This effectively OR's together the inferior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        return self._graph.superior_tasks_subgraph_multi(
            tasks, stop_condition=stop_condition
        )

    def has_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a path from source to target tasks."""
        return self._graph.has_path(source_task, target_task)

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph(source_task, target_task)

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
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
