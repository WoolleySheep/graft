"""Task Dependency Graph and associated classes/exceptions."""

from __future__ import annotations

import functools
from collections.abc import Callable, Generator, Iterable, Iterator, Set
from typing import Any, ParamSpec, Protocol, TypeVar

from graft import graphs
from graft.domain.tasks import helpers
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.uid import UID, SubgraphTasksView, TasksView


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
    """Raised when adding the dependency introduces a cycle to the graph."""

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


def _reraise_edge_adding_exceptions_as_corresponding_dependency_adding_exceptions(
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_edge_can_be_added exceptions as their corresponding validate_dependency_can_be_added exceptions."""

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
            raise HasDependeeTasksError(
                task=e.node, dependee_tasks=e.predecessors
            ) from e
        except graphs.HasSuccessorsError as e:
            raise HasDependentTasksError(
                task=e.node, dependent_tasks=e.successors
            ) from e

    return wrapper


class GraphDependenciesView(Set[tuple[UID, UID]]):
    """View of the dependencies in a graph."""

    def __init__(self, dependencies: Set[tuple[UID, UID]], /) -> None:
        """Initialise DependenciesView."""
        self._dependencies = dependencies

    def __bool__(self) -> bool:
        """Check if view has any dependencies."""
        return bool(self._dependencies)

    def __len__(self) -> int:
        """Return number of dependencies."""
        return len(self._dependencies)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return isinstance(other, GraphDependenciesView) and set(self) == set(other)

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
        """Return string representation of dependencies."""
        task_dependent_pairs = (
            f"({task}, {dependent_task})" for task, dependent_task in self
        )
        return f"{{{', '.join(task_dependent_pairs)}}}"

    def __repr__(self) -> str:
        """Return string representation of dependencies."""
        task_dependent_pairs = (
            f"({task!r}, {dependent_task!r})" for task, dependent_task in iter(self)
        )
        return f"{self.__class__.__name__}({{{', '.join(task_dependent_pairs)}}})"


class DependencySubgraphDependenciesView(Set[tuple[UID, UID]]):
    """View of subgraph dependencies."""

    def __init__(self, dependencies: graphs.SubgraphEdgesView[UID], /) -> None:
        """Initialise SubgraphDependenciesView."""
        self._dependencies = dependencies

    def __bool__(self) -> bool:
        """Check if view has any dependencies."""
        return bool(self._dependencies)

    def __eq__(self, other: object) -> bool:
        """Check if subgraph dependencies view is equal to other."""
        return isinstance(other, DependencySubgraphDependenciesView) and set(
            self
        ) == set(other)

    def __contains__(self, item: object) -> bool:
        """Check if item is a dependency in the subgraph."""
        return item in self._dependencies

    def __iter__(self) -> Iterator[tuple[UID, UID]]:
        """Return iterator over dependencies in view."""
        return iter(self._dependencies)

    def __len__(self) -> int:
        """Return number of dependencies in view."""
        return len(self._dependencies)

    def contains(
        self, tasks_: Iterable[tuple[UID, UID]]
    ) -> Generator[bool, None, None]:
        """Check if dependencies are in the subgraph.

        Theoretically faster than checking if the subgraph contains multiple
        dependencies one at a time, as can cache the parts of the subgraph
        already searched.
        """
        return self._dependencies.contains(edges=tasks_)


class MultipleStartingTasksDependencySubgraphView:
    """View of a dependency subgraph with multiple starting tasks."""

    def __init__(
        self, subgraph: graphs.MultipleStartingNodesDirectedAcyclicSubgraphView[UID]
    ) -> None:
        """Initialise SubgraphView."""
        self._subgraph = subgraph

    def __bool__(self) -> bool:
        """Check if subgraph is not empty."""
        return bool(self._subgraph)

    def __eq__(self, other: object) -> bool:
        """Check if dependency subgraph view is equal to other."""
        return (
            isinstance(other, MultipleStartingTasksDependencySubgraphView)
            and self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def tasks(self) -> SubgraphTasksView:
        """Return view of tasks in subgraph."""
        return SubgraphTasksView(self._subgraph.nodes())

    def dependencies(self) -> DependencySubgraphDependenciesView:
        """Return view of dependencies in subgraph."""
        return DependencySubgraphDependenciesView(self._subgraph.edges())

    def subgraph(self) -> DependencyGraph:
        """Create a concrete copy of the subgraph."""
        return DependencyGraph(self._subgraph.subgraph())


class SingleStartingTaskDependencySubgraphView(
    MultipleStartingTasksDependencySubgraphView
):
    """View of a dependency subgraph with a single starting task."""

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


class IDependencyGraphView(Protocol):
    """Interface for a view of a graph of task dependencies."""

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
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

    def dependencies(self) -> GraphDependenciesView:
        """Return view of dependencies in graph."""
        ...

    def dependee_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependee-tasks of a task."""
        ...

    def dependent_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependent-tasks of a task."""
        ...

    def following_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView: ...

    def proceeding_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView: ...

    def following_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView: ...

    def proceeding_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView: ...

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
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        ...

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        ...

    def task_dependents_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
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

    @classmethod
    def clone(cls, graph: IDependencyGraphView) -> DependencyGraph:
        """Create a clone of a dependency graph from an interface."""
        clone = cls()
        for task in graph.tasks():
            clone.add_task(task)
        for dependee_task, dependent_task in graph.dependencies():
            clone.add_dependency(dependee_task, dependent_task)
        return clone

    def __init__(self, dag: graphs.DirectedAcyclicGraph[UID] | None = None) -> None:
        """Initialise DependencyGraph."""
        self._dag = dag or graphs.DirectedAcyclicGraph[UID]()

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        return (
            isinstance(other, DependencyGraph)
            and self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        return str(self._dag)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_dependents = (
            f"{task!r}: {{{", ".join(repr(dependent) for dependent in dependents)}}}"
            for task, dependents in self.task_dependents_pairs()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_dependents)}}})"

    @helpers.reraise_node_already_exists_as_task_already_exists()
    def add_task(self, /, task: UID) -> None:
        """Add a task to the graph."""
        self._dag.add_node(task)

    @_reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions
    def validate_task_can_be_removed(self, /, task: UID) -> None:
        """Validate that task can be removed from the graph."""
        self._dag.validate_node_can_be_removed(task)

    @_reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions
    def remove_task(self, /, task: UID) -> None:
        """Remove a task."""
        self._dag.remove_node(task)

    @_reraise_edge_adding_exceptions_as_corresponding_dependency_adding_exceptions
    def validate_dependency_can_be_added(
        self, dependee_task: UID, dependent_task: UID, /
    ) -> None:
        """Validate that dependency can be added to the graph."""
        self._dag.validate_edge_can_be_added(
            source=dependee_task, target=dependent_task
        )

    @_reraise_edge_adding_exceptions_as_corresponding_dependency_adding_exceptions
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

    def tasks(self) -> TasksView:
        """Return a view of the tasks."""
        return TasksView(self._dag.nodes())

    def dependencies(self) -> GraphDependenciesView:
        """Return a view of the dependencies."""
        return GraphDependenciesView(self._dag.edges())

    def dependee_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependee-tasks of a task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            dependee_tasks = self._dag.predecessors(task)
        return TasksView(dependee_tasks)

    def dependent_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependent-tasks of a task."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            dependent_tasks = self._dag.successors(task)
        return TasksView(dependent_tasks)

    def following_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            descendants = self._dag.descendants(task, stop_condition=stop_condition)
        return SingleStartingTaskDependencySubgraphView(descendants)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def proceeding_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            ancestors = self._dag.ancestors(task, stop_condition=stop_condition)
        return SingleStartingTaskDependencySubgraphView(ancestors)

    def following_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            following_tasks = self._dag.descendants_multi(
                tasks, stop_condition=stop_condition
            )
        return MultipleStartingTasksDependencySubgraphView(subgraph=following_tasks)

    def proceeding_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView:
        """Return subgraph of proceeding tasks of multiple tasks."""
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            proceeding_tasks = self._dag.ancestors_multi(
                tasks, stop_condition=stop_condition
            )
        return MultipleStartingTasksDependencySubgraphView(subgraph=proceeding_tasks)

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
        return self._dag.has_path(
            source=source_task, target=target_task, stop_condition=stop_condition
        )

    def connecting_subgraph(
        self, source_task: UID, target_task: UID, /
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self.connecting_subgraph_multi(
            source_tasks=[source_task], target_tasks=[target_task]
        )

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        try:
            connecting_subgraph = self._dag.connecting_subgraph_multi(
                sources=source_tasks, targets=target_tasks
            )
        except graphs.NodeDoesNotExistError as e:
            raise TaskDoesNotExistError(task=e.node) from e
        except graphs.NoConnectingSubgraphError as e:
            raise NoConnectingDependencySubgraphError(
                sources=source_tasks, targets=target_tasks
            ) from e

        return DependencyGraph(dag=connecting_subgraph)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependees."""
        return self._dag.is_root(task)

    def first_tasks(self) -> Generator[UID, None, None]:
        """Return generator of first tasks."""
        return self._dag.roots()

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_last(self, task: UID, /) -> bool:
        """Check if task has no dependents."""
        return self._dag.is_leaf(task)

    def last_tasks(self) -> Generator[UID, None, None]:
        """Return generator of last tasks."""
        return self._dag.leaves()

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_isolated(self, task: UID, /) -> bool:
        """Check if task has no dependents nor dependees."""
        return self._dag.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._dag.isolated_nodes()

    def task_dependents_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
        """Return generator over task-dependents pairs."""
        for task, dependents in self._dag.node_successors_pairs():
            yield task, TasksView(dependents)


class DependencyGraphView:
    """View of the DependencyGraph."""

    def __init__(self, dependency_graph: IDependencyGraphView) -> None:
        """Initialise DependencyGraphView."""
        self._graph = dependency_graph

    def __bool__(self) -> bool:
        """Check if view is not empty."""
        return bool(self._graph)

    def __eq__(self, other: object) -> bool:
        """Check if two views are equal."""
        return (
            isinstance(other, DependencyGraphView)
            and self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        tasks_with_dependents = (
            f"{task}: {{{", ".join(str(dependent) for dependent in dependents)}}}"
            for task, dependents in self.task_dependents_pairs()
        )
        return f"{{{', '.join(tasks_with_dependents)}}}"

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_dependents = (
            f"{task!r}: {{{", ".join(repr(dependent) for dependent in dependents)}}}"
            for task, dependents in self.task_dependents_pairs()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_dependents)}}})"

    def tasks(self) -> TasksView:
        """Return view of tasks in graph."""
        return self._graph.tasks()

    def dependencies(self) -> GraphDependenciesView:
        """Return view of dependencies in graph."""
        return self._graph.dependencies()

    def dependee_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependee-tasks of a task."""
        return self._graph.dependee_tasks(task)

    def dependent_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependent-tasks of a task."""
        return self._graph.dependent_tasks(task)

    def following_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView:
        """Yield following tasks of task, following the specified search order."""
        return self._graph.following_tasks(task, stop_condition=stop_condition)

    def proceeding_tasks(
        self,
        task: UID,
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> SingleStartingTaskDependencySubgraphView:
        """Yield proceeding tasks of task, following the specified search order."""
        return self._graph.proceeding_tasks(task, stop_condition=stop_condition)

    def following_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView:
        return self._graph.following_tasks_multi(tasks, stop_condition=stop_condition)

    def proceeding_tasks_multi(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> MultipleStartingTasksDependencySubgraphView:
        return self._graph.proceeding_tasks_multi(tasks, stop_condition=stop_condition)

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
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph(source_task, target_task)

    def connecting_subgraph_multi(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph_multi(source_tasks, target_tasks)

    def task_dependents_pairs(self) -> Generator[tuple[UID, TasksView], None, None]:
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
