"""Task Dependency Graph and associated classes/exceptions."""

from collections.abc import Generator, Iterator, Set

from graft import graphs
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.uid import UID, UIDsView


class DependenciesView(Set[tuple[UID, UID]]):
    """View of the dependencies in a graph."""

    def __init__(self, dependencies: Set[tuple[UID, UID]], /) -> None:
        """Initialise DependenciesView."""
        self._dependencies = dependencies

    def __bool__(self) -> bool:
        """Check view has any dependencies."""
        return bool(self._dependencies)

    def __len__(self) -> int:
        """Return number of dependencies."""
        return len(self._dependencies)

    def __contains__(self, item: object) -> bool:
        """Check if item in DependenciesView."""
        try:
            return item in self._dependencies
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return generator over dependencies in view."""
        return iter(self._dependencies)

    def __str__(self) -> str:
        """Return string representation of view."""
        formatted_dependencies = (
            f"({dependee}, {dependent})" for dependee, dependent in self
        )
        return f"dependencies_view({', '.join(formatted_dependencies)})"


class DependencyGraph:
    """Graph of task dependencies.

    Shows which tasks have to be completed before another task can be started.

    Acts as a DAG.
    """

    def __init__(self, dag: graphs.DirectedAcyclicGraph[UID]) -> None:
        """Initialise Hierarchies."""
        self._dag = dag

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in graph."""
        return iter(self._dag)

    def __contains__(self, item: object) -> bool:
        """Check if item in graph."""
        return item in self._dag

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        try:
            self._dag.add_node(task)
        except graphs.NodeAlreadyExistsError as e:
            raise TaskAlreadyExistsError(task) from e

    def tasks(self) -> UIDsView:
        """Return a view of the tasks."""
        return UIDsView(self._dag.nodes())

    def dependencies(self) -> DependenciesView:
        """Return a view of the dependencies."""
        return DependenciesView(self._dag.edges())

    def dependees(self, task: UID) -> UIDsView:
        """Return a view of the dependees of a task."""
        try:
            return UIDsView(self._dag.predecessors(task))
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e

    def dependents(self, task: UID) -> UIDsView:
        """Return a view of the dependents of a task."""
        try:
            return UIDsView(self._dag.successors(task))
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e

    def task_dependents_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-dependents pairs."""
        for task, dependents in self._dag.node_successors_pairs():
            yield task, UIDsView(dependents)


class DependencyGraphView:
    """View of the DependencyGraph."""

    def __init__(self, dependency_graph: DependencyGraph) -> None:
        """Initialise DependencyGraphView."""
        self._dependency_graph = dependency_graph

    def __bool__(self) -> bool:
        """Check view has any tasks."""
        return bool(self._dependency_graph)

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in view."""
        return iter(self._dependency_graph)

    def __contains__(self, item: object) -> bool:
        """Check if item in graph view."""
        return item in self._dependency_graph

    def task_dependents_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-dependents pairs."""
        return self._dependency_graph.task_dependents_pairs()
