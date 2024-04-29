"""Hierarchy Graph and associated classes/exceptions."""


import copy
from collections.abc import Callable, Generator, Iterable, Iterator, Set
from typing import Any, Protocol, Self

from graft import graphs
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.uid import (
    UID,
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


class InverseHierarchyAlreadyExistsError(Exception):
    """Raised when an inverse hierarchy between specified tasks already exists."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize InverseHierarchyAlreadyExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        super().__init__(
            f"Inverse hierarchy between supertask [{subtask}] and subtask [{supertask}] already exists",
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
        connecting_subgraph: "HierarchyGraph",
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


class HierarchyPathAlreadyExistsError(Exception):
    """Path already exists from supertask to subtask."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        connecting_subgraph: "HierarchyGraph",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize HierarchyPathAlreadyExistsError."""
        self.supertask = supertask
        self.subtask = subtask
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"hierarchy path already exists between supertask [{supertask}] and subtask [{subtask}]",
            *args,
            **kwargs,
        )


class SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError(Exception):
    """Subtask is already a sub-task of one or more of the super-task's superior tasks."""

    def __init__(
        self,
        supertask: UID,
        subtask: UID,
        subgraph: "HierarchyGraph",
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError."""
        self.supertask = supertask
        self.subtask = subtask
        self.subgraph = subgraph
        super().__init__(
            (
                f"sub-task [{subtask}] is already a sub-task of one or more of "
                f"supertask [{supertask}]'s superior tasks"
            ),
            *args,
            **kwargs,
        )


class HierarchiesView(Set[tuple[UID, UID]]):
    """View of the hierarchies in the graph."""

    def __init__(self, heirarchies: Set[tuple[UID, UID]], /) -> None:
        """Initialise HierarchiesView."""
        self._hierarchies = heirarchies

    def __bool__(self) -> bool:
        """Check view has any hierarchies."""
        return bool(self._hierarchies)

    def __len__(self) -> int:
        """Return number of hierarchies."""
        return len(self._hierarchies)

    def __contains__(self, item: object) -> bool:
        """Check if item in HierarchiesView."""
        # TODO: Doesn't make sense to catch this error for generic self._heirarchies
        try:
            return item in self._hierarchies
        except graphs.NodeDoesNotExistError[UID] as e:
            raise TaskDoesNotExistError(e.node) from e

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return generator over hierarchies in view."""
        return iter(self._hierarchies)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return isinstance(other, HierarchiesView) and set(self) == set(other)

    def __str__(self) -> str:
        """Return string representation of view."""
        formatted_hierarchies = (
            f"({supertask}, {subtask})" for supertask, subtask in self
        )
        return f"hierarchies_view({', '.join(formatted_hierarchies)})"


class IHierarchyGraphView(Protocol):
    """Interface for a view of a graph of task hierarchies."""

    def __bool__(self) -> bool:
        """Check if graph has any tasks."""
        ...

    def __contains__(self, item: object) -> bool:
        """Check if item in graph."""
        ...

    def __len__(self) -> int:
        """Return number of tasks in graph."""
        ...

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        ...

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in graph."""
        ...

    def __str__(self) -> str:
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

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-subtasks pairs."""
        ...

    def is_concrete(self, task: UID) -> bool:
        """Check if task is concrete."""
        ...


class HierarchyGraph:
    """Graph of task hierarchies.

    Shows which tasks are subtasks of other tasks.

    Acts as a Minimum DAG.
    """

    def __init__(self, reduced_dag: graphs.ReducedDAG[UID] | None = None) -> None:
        """Initialise HierarchyGraph."""
        self._reduced_dag = (
            copy.deepcopy(reduced_dag) if reduced_dag else graphs.ReducedDAG[UID]()
        )

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in graph."""
        return iter(self._reduced_dag)

    def __contains__(self, item: object) -> bool:
        """Check if item in graph."""
        return item in self._reduced_dag

    def __len__(self) -> int:
        """Return number of tasks in graph."""
        return len(self._reduced_dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        return (
            isinstance(other, HierarchyGraph)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = list[str]()
        for task, subtasks in self._reduced_dag.node_successors_pairs():
            tasks_with_subtasks.append(
                f"{task}: {{{', '.join(str(value) for value in subtasks)}}}",
            )
        return f"hierarchy_graph({{{', '.join(tasks_with_subtasks)}}})"

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        return UIDsView(self._reduced_dag.nodes())

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        return HierarchiesView(self._reduced_dag.edges())

    def supertasks(self, task: UID, /) -> UIDsView:
        """Return view of supertasks of task."""
        try:
            supertasks = self._reduced_dag.predecessors(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

        return UIDsView(supertasks)

    def subtasks(self, task: UID, /) -> UIDsView:
        """Return view of subtasks of task."""
        try:
            subtasks = self._reduced_dag.successors(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

        return UIDsView(subtasks)

    def inferior_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of inferior tasks of task."""
        try:
            return self._reduced_dag.descendants_bfs(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

    def inferior_tasks_dfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return depth-first search of inferior tasks of task."""
        try:
            return self._reduced_dag.descendants_dfs(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

    def superior_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of superior tasks of task."""
        try:
            return self._reduced_dag.ancestors_bfs(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

    def superior_tasks_dfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return depth-first search of superior tasks of task."""
        try:
            return self._reduced_dag.ancestors_dfs(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

    def inferior_tasks_subgraph(
        self, task: UID, /, stop_condition: Callable[[UID], bool] | None = None
    ) -> Self:
        """Return subgraph of inferior tasks of task.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        try:
            inferior_tasks_subgraph = self._reduced_dag.descendants_subgraph(
                task, stop_condition=stop_condition
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e
        return type(self)(inferior_tasks_subgraph)

    def superior_tasks_subgraph(
        self, task: UID, /, stop_condition: Callable[[UID], bool] | None = None
    ) -> Self:
        """Return subgraph of superior tasks of task.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        try:
            superior_tasks_subgraph = self._reduced_dag.ancestors_subgraph(
                task, stop_condition=stop_condition
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e
        return type(self)(superior_tasks_subgraph)

    def inferior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Self:
        """Return subgraph of inferior tasks of multiple tasks.

        This effectively OR's together the superior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        try:
            inferior_tasks_subgraph = self._reduced_dag.descendants_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e
        return type(self)(inferior_tasks_subgraph)

    def superior_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Self:
        """Return subgraph of superior tasks of multiple tasks.

        This effectively OR's together the inferior-task subgraphs of several
        tasks.

        The original tasks are part of the subgraph.

        Stop searching beyond a specific task if the stop condition is met. If
        the starting task meets the stop condition, this will be ignored.
        """
        try:
            superior_tasks_subgraph = self._reduced_dag.ancestors_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e
        return type(self)(superior_tasks_subgraph)

    def has_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a path from source to target tasks."""
        try:
            return self._reduced_dag.has_path(source=source_task, target=target_task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e

    def connecting_subgraph(self, source_task: UID, target_task: UID, /) -> Self:
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

        return type(self)(connecting_subgraph)

    def add_task(self, task: UID, /) -> None:
        """Add a task."""
        try:
            self._reduced_dag.add_node(task)
        except graphs.NodeAlreadyExistsError as e:
            raise TaskAlreadyExistsError(task) from e

    def remove_task(self, task: UID, /) -> None:
        """Remove a task."""
        try:
            self._reduced_dag.remove_node(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e
        except graphs.HasPredecessorsError as e:
            raise HasSuperTasksError(task=task, supertasks=e.predecessors) from e
        except graphs.HasSuccessorsError as e:
            raise HasSubTasksError(task=task, subtasks=e.successors) from e

    def add_hierarchy(self, supertask: UID, subtask: UID, /) -> None:
        """Add a hierarchy between the specified tasks."""
        try:
            self._reduced_dag.add_edge(source=supertask, target=subtask)
        except graphs.LoopError as e:
            raise HierarchyLoopError(supertask) from e
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            raise HierarchyAlreadyExistsError(supertask, subtask) from e
        except graphs.InverseEdgeAlreadyExistsError as e:
            raise InverseHierarchyAlreadyExistsError(supertask, subtask) from e

        except graphs.IntroducesCycleError as e:
            connecting_subgraph = HierarchyGraph(e.connecting_subgraph)
            raise HierarchyIntroducesCycleError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            ) from e

        except graphs.PathAlreadyExistsError as e:
            connecting_subgraph = HierarchyGraph(e.connecting_subgraph)
            raise HierarchyPathAlreadyExistsError(
                supertask=supertask,
                subtask=subtask,
                connecting_subgraph=connecting_subgraph,
            ) from e

        except graphs.TargetAlreadySuccessorOfSourceAncestorsError as e:
            subgraph = HierarchyGraph(e.subgraph)
            raise SubTaskIsAlreadySubTaskOfSuperiorTaskOfSuperTaskError(
                supertask=supertask, subtask=subtask, subgraph=subgraph
            ) from e

    def remove_hierarchy(self, supertask: UID, subtask: UID, /) -> None:
        """Remove the hierarchy between the specified tasks."""
        try:
            self._reduced_dag.remove_edge(source=supertask, target=subtask)
        except graphs.LoopError as e:
            raise HierarchyLoopError(supertask) from e
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e
        except graphs.EdgeDoesNotExistError as e:
            raise HierarchyDoesNotExistError(supertask, subtask) from e

    def is_concrete(self, task: UID, /) -> bool:
        """Check if task is concrete.

        Concrete tasks have no sub-tasks.
        """
        try:
            return self._reduced_dag.is_leaf(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e

    def concrete_tasks(self) -> Generator[UID, None, None]:
        """Return generator over concrete tasks."""
        return self._reduced_dag.leaves()

    def is_top_level(self, task: UID, /) -> bool:
        """Check if task is top-level.

        Top-level tasks have no super-tasks.
        """
        try:
            return self._reduced_dag.is_root(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e

    def top_level_tasks(self) -> Generator[UID, None, None]:
        """Return generator over top-level tasks."""
        return self._reduced_dag.roots()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no super-tasks nor sub-tasks."""
        try:
            return self._reduced_dag.is_isolated(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e

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
        """Check view has any tasks."""
        return bool(self._graph)

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in view."""
        return iter(self._graph)

    def __len__(self) -> int:
        """Return number of tasks in view."""
        return len(self._graph)

    def __eq__(self, other: object) -> bool:
        """Check if two hierarchy graph views are equal."""
        return (
            isinstance(other, HierarchyGraphView)
            and self.tasks() == other.tasks()
            and self.hierarchies() == other.hierarchies()
        )

    def __contains__(self, item: object) -> bool:
        """Check if item in graph view."""
        return item in self._graph

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

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-subtasks pairs."""
        return self._graph.task_subtasks_pairs()

    def is_concrete(self, task: UID) -> bool:
        """Check if task is concrete."""
        return self._graph.is_concrete(task)
