"""Task Dependency Graph and associated classes/exceptions."""

from __future__ import annotations

import functools
from collections.abc import Callable, Generator, Iterable, Iterator, Set
from typing import Any, ParamSpec, Protocol, TypeVar

from graft import graphs
from graft.domain.tasks import helpers
from graft.domain.tasks.helpers import TaskAlreadyExistsError, TaskDoesNotExistError
from graft.domain.tasks.uid import UID, UIDsView


class HasDependeeTasksError(Exception):
    """Raised when a task has dependee-tasks."""

    def __init__(
        self,
        task: UID,
        dependee_tasks: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HasDependeeTasksError."""
        self.task = task
        self.dependee_tasks = set(dependee_tasks)
        formatted_dependee_tasks = (
            str(dependee_task) for dependee_task in dependee_tasks
        )
        super().__init__(
            f"Task [{task}] has dependee-tasks [{", ".join(formatted_dependee_tasks)}]",
            *args,
            **kwargs,
        )


class HasDependentTasksError(Exception):
    """Raised when a task has dependent-tasks."""

    def __init__(
        self,
        task: UID,
        dependent_tasks: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise HasDependentTasksError."""
        self.task = task
        self.dependent_tasks = set(dependent_tasks)
        formatted_dependent_tasks = (
            str(dependent_task) for dependent_task in dependent_tasks
        )
        super().__init__(
            f"Task [{task}] has sub-tasks [{", ".join(formatted_dependent_tasks)}]",
            *args,
            **kwargs,
        )


class DependencyAlreadyExistsError(Exception):
    """Raised when a dependency between specified tasks already exists."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyAlreadyExistsError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}] already exists",
            *args,
            **kwargs,
        )


class DependencyDoesNotExistError(Exception):
    """Raised when a dependency between specified tasks does not exist."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialise DependencyDoesNotExistError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        super().__init__(
            f"Dependency between dependee-task [{dependee_task}] and dependent-task [{dependent_task}] does not exist",
            *args,
            **kwargs,
        )


class DependencyLoopError(Exception):
    """Loop error.

    Raised when a dependency is referenced that connects a task to itself, creating a
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
        super().__init__(f"Dependency loop [{task}]", *args, **kwargs)


class NoConnectingDependencySubgraphError(Exception):
    """Raised when no connecting subgraph exists."""

    def __init__(
        self,
        sources: Iterable[UID],
        targets: Iterable[UID],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize NoConnectingDependencySubgraphError."""
        self.sources = list(sources)
        self.targets = list(targets)

        formatted_sources = ", ".join(str(source) for source in sources)
        formatted_targets = ", ".join(str(target) for target in targets)
        super().__init__(
            f"no connecting subgraph from tasks [{formatted_sources}] to tasks [{formatted_targets}] exists",
            *args,
            **kwargs,
        )


class DependencyIntroducesCycleError(Exception):
    """Adding the dependency introduces a cycle to the graph."""

    def __init__(
        self,
        dependee_task: UID,
        dependent_task: UID,
        connecting_subgraph: DependencyGraph,
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize DependencyIntroducesCycleError."""
        self.dependee_task = dependee_task
        self.dependent_task = dependent_task
        self.connecting_subgraph = connecting_subgraph
        super().__init__(
            f"Dependency from [{dependee_task}] to [{dependent_task}] introduces cycle",
            *args,
            **kwargs,
        )


P = ParamSpec("P")
R = TypeVar("R")


def reraise_graph_exceptions_as_dependency_exceptions(
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise graph exceptions as their corresponding dependency exceptions."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            raise DependencyLoopError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            raise DependencyAlreadyExistsError(e.source, e.target) from e
        except graphs.IntroducesCycleError as e:
            raise DependencyIntroducesCycleError(
                dependee_task=e.source,
                dependent_task=e.target,
                connecting_subgraph=DependencyGraph(e.connecting_subgraph),
            ) from e

    return wrapper


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

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return isinstance(other, DependenciesView) and set(self) == set(other)

    def __contains__(self, item: object) -> bool:
        """Check if item in DependenciesView."""
        # TODO: Doesn't make sense to catch this error for generic self._dependencies
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


class IDependencyGraphView(Protocol):
    """Interface for a view of a graph of task dependencies."""

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

    def dependencies(self) -> DependenciesView:
        """Return view of dependencies in graph."""
        ...

    def dependee_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependee-tasks of a task."""
        ...

    def dependent_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependent-tasks of a task."""
        ...

    def task_dependents_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-dependents pairs."""
        ...

    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependees."""
        ...

    def first_tasks(self) -> Generator[UID, None, None]:
        """Return generator of first tasks."""
        ...

    def is_last(self, task: UID, /) -> bool:
        """Check if task has no dependents."""
        ...

    def last_tasks(self) -> Generator[UID, None, None]:
        """Return generator of last tasks."""
        ...

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependents nor dependees."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        ...


class DependencyGraph:
    """Graph of task dependencies.

    Shows which tasks have to be completed before another task can be started.

    Acts as a DAG.
    """

    def __init__(self, dag: graphs.DirectedAcyclicGraph[UID] | None = None) -> None:
        """Initialise DependencyGraph."""
        self._dag = dag or graphs.DirectedAcyclicGraph[UID]()

    def __bool__(self) -> bool:
        """Check if graph has any tasks."""
        return bool(self._dag)

    def __iter__(self) -> Iterator[UID]:
        """Return generator over tasks in graph."""
        return iter(self._dag)

    def __len__(self) -> int:
        """Return number of tasks in graph."""
        return len(self._dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        return (
            isinstance(other, DependencyGraph)
            and self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def __contains__(self, item: object) -> bool:
        """Check if item in graph."""
        return item in self._dag

    def add_task(self, /, task: UID) -> None:
        """Add a task."""
        try:
            self._dag.add_node(task)
        except graphs.NodeAlreadyExistsError as e:
            raise TaskAlreadyExistsError(task) from e

    def remove_task(self, /, task: UID) -> None:
        """Remove a task."""
        try:
            self._dag.remove_node(task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task) from e
        except graphs.HasPredecessorsError as e:
            raise HasDependeeTasksError(task=task, dependee_tasks=e.predecessors) from e
        except graphs.HasSuccessorsError as e:
            raise HasDependentTasksError(task=task, dependent_tasks=e.successors) from e

    @reraise_graph_exceptions_as_dependency_exceptions
    def validate_dependency_can_be_added(
        self, dependee_task: UID, dependent_task: UID, /
    ) -> None:
        """Validate that dependency can be added to the graph."""
        self._dag.validate_edge_can_be_added(
            source=dependee_task, target=dependent_task
        )

    @reraise_graph_exceptions_as_dependency_exceptions
    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Add a dependency between two tasks."""
        self._dag.add_edge(source=dependee_task, target=dependent_task)

    def remove_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        """Remove the dependency between the specified tasks."""
        try:
            self._dag.remove_edge(source=dependee_task, target=dependent_task)
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            raise DependencyLoopError(e.node) from e
        except graphs.EdgeDoesNotExistError as e:
            raise DependencyDoesNotExistError(dependee_task, dependent_task) from e

    def tasks(self) -> UIDsView:
        """Return a view of the tasks."""
        return UIDsView(self._dag.nodes())

    def dependencies(self) -> DependenciesView:
        """Return a view of the dependencies."""
        return DependenciesView(self._dag.edges())

    def dependee_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependee-tasks of a task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            dependee_tasks = self._dag.predecessors(task)
        return UIDsView(dependee_tasks)

    def dependent_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependent-tasks of a task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            dependent_tasks = self._dag.successors(task)
        return UIDsView(dependent_tasks)

    def following_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of following tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.descendants_bfs(task)

    def following_tasks_dfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return depth-first search of following tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.descendants_dfs(task)

    def proceeding_tasks_bfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return breadth-first search of proceeding tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.ancestors_bfs(task)

    def proceeding_tasks_dfs(self, task: UID, /) -> Generator[UID, None, None]:
        """Return depth-first search of proceeding tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.ancestors_dfs(task)

    def following_tasks_subgraph(
        self, task: UID, /, stop_condition: Callable[[UID], bool] | None = None
    ) -> DependencyGraph:
        """Return subgraph of following tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            following_tasks_subgraph = self._dag.descendants_subgraph(
                task, stop_condition=stop_condition
            )
        return DependencyGraph(dag=following_tasks_subgraph)

    def following_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        """Return subgraph of following tasks of multiple tasks."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            following_tasks_subgraph = self._dag.descendants_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        return DependencyGraph(dag=following_tasks_subgraph)

    def proceeding_tasks_subgraph(
        self, task: UID, /, stop_condition: Callable[[UID], bool] | None = None
    ) -> DependencyGraph:
        """Return subgraph of proceeding tasks of task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            proceeding_tasks_subgraph = self._dag.ancestors_subgraph(
                task, stop_condition=stop_condition
            )
        return DependencyGraph(dag=proceeding_tasks_subgraph)

    def proceeding_tasks_subgraph_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        """Return subgraph of proceeding tasks of multiple tasks."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            proceeding_tasks_subgraph = self._dag.ancestors_subgraph_multi(
                tasks, stop_condition=stop_condition
            )
        return DependencyGraph(dag=proceeding_tasks_subgraph)

    def has_path(self, source_task: UID, target_task: UID, /) -> bool:
        """Check if there is a path from source to target tasks."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.has_path(source=source_task, target=target_task)

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        try:
            connecting_subgraph = self._dag.connecting_subgraph(
                source=source_task, target=target_task
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e
        except graphs.NoConnectingSubgraphError as e:
            raise NoConnectingDependencySubgraphError(
                sources=[source_task], targets=[target_task]
            ) from e

        return DependencyGraph(dag=connecting_subgraph)

    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependees."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.is_root(task)

    def first_tasks(self) -> Generator[UID, None, None]:
        """Return generator of first tasks."""
        return self._dag.roots()

    def is_last(self, task: UID, /) -> bool:
        """Check if task has no dependents."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.is_leaf(task)

    def last_tasks(self) -> Generator[UID, None, None]:
        """Return generator of last tasks."""
        return self._dag.leaves()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependents nor dependees."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            return self._dag.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._dag.isolated_nodes()

    def task_dependents_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-dependents pairs."""
        for task, dependents in self._dag.node_successors_pairs():
            yield task, UIDsView(dependents)


class DependencyGraphView:
    """View of the DependencyGraph."""

    def __init__(self, dependency_graph: IDependencyGraphView) -> None:
        """Initialise DependencyGraphView."""
        self._graph = dependency_graph

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
        """Check if two views are equal."""
        return (
            isinstance(other, DependencyGraphView)
            and self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def __contains__(self, item: object) -> bool:
        """Check if item in graph view."""
        return item in self._graph

    def tasks(self) -> UIDsView:
        """Return view of tasks in graph."""
        return self._graph.tasks()

    def dependencies(self) -> DependenciesView:
        """Return view of dependencies in graph."""
        return self._graph.dependencies()

    def dependee_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependee-tasks of a task."""
        return self._graph.dependee_tasks(task)

    def dependent_tasks(self, task: UID, /) -> UIDsView:
        """Return a view of the dependent-tasks of a task."""
        return self._graph.dependent_tasks(task)

    def task_dependents_pairs(self) -> Generator[tuple[UID, UIDsView], None, None]:
        """Return generator over task-dependents pairs."""
        return self._graph.task_dependents_pairs()

    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependees."""
        return self._graph.is_first(task)

    def first_tasks(self) -> Generator[UID, None, None]:
        """Return generator of first tasks."""
        return self._graph.first_tasks()

    def is_last(self, task: UID, /) -> bool:
        """Check if task has no dependents."""
        return self._graph.is_last(task)

    def last_tasks(self) -> Generator[UID, None, None]:
        """Return generator of last tasks."""
        return self._graph.last_tasks()

    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependents nor dependees."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._graph.isolated_tasks()
