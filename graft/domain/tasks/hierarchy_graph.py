"""Hierarchy Graph and associated classes/exceptions."""


from collections.abc import Generator, Iterable, Iterator, Set

from graft import graphs
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.uid import (
    UID,
    UIDsView,
)


class HasSuperTasksError(Exception):
    """Raised when a task has super-tasks."""

    def __init__(self, task: UID, supertasks: Iterable[UID]) -> None:
        """Initialise HasSuperTasksError."""
        self.task = task
        self.supertasks = set(supertasks)
        formatted_supertasks = (str(supertask) for supertask in supertasks)
        super().__init__(
            f"Task [{task}] has super-tasks [{", ".join(formatted_supertasks)}]"
        )


class HasSubTasksError(Exception):
    """Raised when a task has sub-tasks."""

    def __init__(self, task: UID, subtasks: Iterable[UID]) -> None:
        """Initialise HasSubTasksError."""
        self.task = task
        self.subtasks = set(subtasks)
        formatted_subtasks = (str(task) for task in subtasks)
        super().__init__(
            f"Task [{task}] has sub-tasks [{", ".join(formatted_subtasks)}]"
        )


class HierarchiesView(Set[tuple[UID, UID]]):
    """View of the hierarchies in the graph."""

    def __init__(self, hirarchies: Set[tuple[UID, UID]], /) -> None:
        """Initialise HierarchiesView."""
        self._hierarchies = hirarchies

    def __bool__(self) -> bool:
        """Check view has any hierarchies."""
        return bool(self._hierarchies)

    def __len__(self) -> int:
        """Return number of hierarchies."""
        return len(self._hierarchies)

    def __contains__(self, item: object) -> bool:
        """Check if item in HierarchiesView."""
        try:
            return item in self._hierarchies
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return generator over hierarchies in view."""
        return iter(self._hierarchies)

    def __str__(self) -> str:
        """Return string representation of view."""
        formatted_hierarchies = (
            f"({supertask}, {subtask})" for supertask, subtask in self
        )
        return f"hierarchies_view({', '.join(formatted_hierarchies)})"


class HierarchyGraph:
    """Graph of task hierarchies.

    Shows which tasks are subtasks of other tasks.

    Acts as a Minimum DAG.
    """

    def __init__(self, min_dag: graphs.MinimumDAG[UID]) -> None:
        """Initialise HierarchyGraph."""
        self._min_dag = min_dag

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in graph."""
        return iter(self._min_dag)

    def __contains__(self, item: object) -> bool:
        """Check if item in graph."""
        return item in self._min_dag

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        return UIDsView(self._min_dag.nodes())

    def supertasks(self, /, task: UID) -> UIDsView:
        """Return view of supertasks of task."""
        try:
            supertasks = self._min_dag.predecessors(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

        return UIDsView(supertasks)

    def subtasks(self, /, task: UID) -> UIDsView:
        """Return view of subtasks of task."""
        try:
            subtasks = self._min_dag.successors(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=task) from e

        return UIDsView(subtasks)

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        try:
            self._min_dag.add_node(task)
        except graphs.NodeAlreadyExistsError as e:
            raise TaskAlreadyExistsError(task) from e

    def remove_task(self, /, task: UID) -> None:
        """Remove a task."""
        try:
            self._min_dag.remove_node(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e
        except graphs.HasPredecessorsError as e:
            raise HasSuperTasksError(task=task, supertasks=e.predecessors) from e
        except graphs.HasSuccessorsError as e:
            raise HasSubTasksError(task=task, subtasks=e.successors) from e

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        return HierarchiesView(self._min_dag.edges())

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-subtasks pairs."""
        for task, subtasks in self._min_dag.node_successors_pairs():
            yield task, UIDsView(subtasks)


class HierarchyGraphView:
    """View of the HierarchyGraph."""

    def __init__(self, hierarchy_graph: HierarchyGraph) -> None:
        """Initialise HierarchyGraphView."""
        self._hierarchy_graph = hierarchy_graph

    def __bool__(self) -> bool:
        """Check view has any tasks."""
        return bool(self._hierarchy_graph)

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in view."""
        return iter(self._hierarchy_graph)

    def __contains__(self, item: object) -> bool:
        """Check if item in graph view."""
        return item in self._hierarchy_graph

    def task_subtasks_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-subtasks pairs."""
        return self._hierarchy_graph.task_subtasks_pairs()
