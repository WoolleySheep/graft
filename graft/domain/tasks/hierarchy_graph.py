from collections.abc import Generator, Iterator

from graft import graphs
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.uid import (
    UID,
    UIDsView,
)


class HierarchiesView:
    """View of a set of hierarchies."""

    def __init__(self, min_dag: graphs.MinimumDAG[UID]) -> None:
        """Initialise HierarchiesView."""
        self._min_dag = min_dag

    def __bool__(self) -> bool:
        """Check view has any hierarchies."""
        return bool(self._min_dag.edges())

    def __len__(self) -> int:
        """Return number of hierarchies."""
        return len(self._min_dag.edges())

    def __contains__(self, item: object) -> bool:
        """Check if item in HierarchiesView."""
        try:
            return item in self._min_dag.edges()
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e

    def __iter__(self) -> Generator[tuple[UID, UID], None, None]:
        """Return generator over hierarchies in view."""
        return iter(self._min_dag.edges())

    def __str__(self) -> str:
        """Return string representation of view."""
        hierarchies = iter(self)
        formatted_hierarchies = (
            f"({supertask}, {subtask})" for supertask, subtask in hierarchies
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
        return UIDsView(self._min_dag.predecessors(task))

    def subtasks(self, /, task: UID) -> UIDsView:
        """Return view of subtasks of task."""
        return UIDsView(self._min_dag.successors(task))

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        try:
            self._min_dag.add_node(task)
        except graphs.NodeAlreadyExistsError as e:
            raise TaskAlreadyExistsError(task) from e

    def hierarchies(self) -> HierarchiesView:
        """Return a view of the hierarchies."""
        return HierarchiesView(min_dag=self._min_dag)

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
