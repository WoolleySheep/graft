"""Task Dependency Graph and associated classes/exceptions."""

from __future__ import annotations

import copy
import functools
import itertools
from collections.abc import (
    Hashable,
    Set,
)
from typing import TYPE_CHECKING, Any, Protocol, TypeGuard

from graft import graphs
from graft.domain.tasks import helpers
from graft.domain.tasks.helpers import TaskDoesNotExistError
from graft.domain.tasks.uid import UID, TasksView
from graft.graphs import (
    ConnectionsDictHasCycleError,
    ConnectionsDictNodesHaveLoops,
    TargetsAreNotNotAlsoSourceNodesError,
)
from graft.graphs.directed_acyclic_graph import DirectedAcyclicGraph

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
        Iterable,
        Iterator,
        Mapping,
    )


class HasDependencyNeighboursError(Exception):
    """Raised when a task has neighbours.

    A task cannot be removed when it has any neighbours.
    """

    def __init__(
        self,
        task: UID,
        dependee_tasks: Iterable[UID],
        dependent_tasks: Iterable[UID],
    ) -> None:
        self.task = task
        self.dependee_tasks = set(dependee_tasks)
        self.dependent_tasks = set(dependent_tasks)
        formatted_neighbours = (
            str(neighbour)
            for neighbour in itertools.chain(self.dependee_tasks, self.dependent_tasks)
        )
        super().__init__(
            f"Task [{task}] has neighbours [{', '.join(formatted_neighbours)}]"
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


class DependentTasksAreNotAlsoDependeeTasksError(Exception):
    """Raised when some dependents are not also dependees."""

    def __init__(
        self,
        dependent_tasks: Iterable[Hashable],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependent_tasks = set(dependent_tasks)
        super().__init__(
            f"dependent tasks [{self.dependent_tasks}] are not also dependee tasks",
            *args,
            **kwargs,
        )


class ConnectionsDictDependencyGraphTasksHaveLoops(Exception):
    """Connections used to construct the graph include loops."""

    def __init__(self, tasks: Iterable[Hashable]) -> None:
        self.tasks = set(tasks)
        formatted_tasks = (str(task) for task in self.tasks)
        super().__init__(
            f"Connections used to construct the graph have loops for tasks [{', '.join(formatted_tasks)}]"
        )


class ConnectionsDictDependencyGraphHasCycleError(Exception):
    """Underlying dictionary has a cycle."""

    def __init__(self, dictionary: Mapping[Any, Set[Any]]) -> None:
        self.dictionary = dict(dictionary)
        super().__init__(f"Underlying dictionary [{dictionary}] has a cycle")


def _is_uid_graph(obj: object) -> TypeGuard[DirectedAcyclicGraph[UID]]:
    return isinstance(obj, DirectedAcyclicGraph) and all(
        isinstance(item, UID)
        for item in obj.nodes()  # type: ignore
    )


def _reraise_edge_adding_exceptions_as_corresponding_dependency_adding_exceptions[
    **P,
    R,
](
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_edge_can_be_added exceptions as their corresponding validate_dependency_can_be_added exceptions."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except graphs.NodeDoesNotExistError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise DependencyLoopError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            if not isinstance(e.source, UID) or not isinstance(e.target, UID):
                raise TypeError from e
            raise DependencyAlreadyExistsError(e.source, e.target) from e
        except graphs.IntroducesCycleError as e:
            if (
                not isinstance(e.source, UID)
                or not isinstance(e.target, UID)
                or not _is_uid_graph(e.connecting_subgraph)
            ):
                raise TypeError from e
            raise DependencyIntroducesCycleError(
                dependee_task=e.source,
                dependent_task=e.target,
                connecting_subgraph=DependencyGraph(
                    (node, e.connecting_subgraph.successors(node))
                    for node in e.connecting_subgraph.nodes()
                ),
            ) from e

    return wrapper


def _is_uid_set(obj: object) -> TypeGuard[set[UID]]:
    return isinstance(obj, set) and all(isinstance(item, UID) for item in obj)  # type: ignore


def _reraise_node_removing_exceptions_as_corresponding_task_removing_exceptions[**P, R](
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_node_can_be_removed exceptions as their corresponding validate_task_can_be_removed exceptions."""

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return fn(*args, **kwargs)
        except graphs.NodeDoesNotExistError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise TaskDoesNotExistError(e.node) from e
        except graphs.HasNeighboursError as e:
            if (
                not isinstance(e.node, UID)
                or not _is_uid_set(e.predecessors)
                or not _is_uid_set(e.successors)
            ):
                raise TypeError from e
            raise HasDependencyNeighboursError(
                task=e.node, dependee_tasks=e.predecessors, dependent_tasks=e.successors
            ) from e

    return wrapper


class DependenciesView(Set[tuple[UID, UID]]):
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
        return isinstance(other, DependenciesView) and set(self) == set(other)

    def __contains__(self, item: object) -> bool:
        """Check if item in DependenciesView."""
        # TODO: Doesn't make sense to catch this error for generic self._dependencies
        try:
            return item in self._dependencies
        except graphs.NodeDoesNotExistError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
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

    def __sub__(self, other: Set[Any]) -> set[tuple[UID, UID]]:
        """Return difference of two views."""
        return set(self._dependencies - other)

    def __and__(self, other: Set[Any]) -> set[tuple[UID, UID]]:
        """Return intersection of two views."""
        return set(self._dependencies & other)

    def __or__[G: Hashable](self, other: Set[G]) -> set[tuple[UID, UID] | G]:
        """Return union of two views."""
        return set(self._dependencies | other)

    def __xor__[G: Hashable](self, other: Set[G]) -> set[tuple[UID, UID] | G]:
        """Return symmetric difference of two views."""
        return set(self._dependencies ^ other)

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return self._dependencies <= other

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self._dependencies < other

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return self._dependencies >= other

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self._dependencies > other


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

    def clone(self) -> DependencyGraph:
        """Create a clone of the dependency graph."""
        ...

    def tasks(self) -> TasksView:
        """Return view of tasks in graph."""
        ...

    def dependencies(self) -> DependenciesView:
        """Return view of dependencies in graph."""
        ...

    def dependee_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependee-tasks of a task."""
        ...

    def dependent_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependent-tasks of a task."""
        ...

    def following_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph: ...

    def following_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]: ...

    def proceeding_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph: ...

    def proceeding_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]: ...

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        ...

    def component_subgraph(self, task: UID) -> DependencyGraph: ...

    def component_subgraphs(self) -> Generator[DependencyGraph, None, None]: ...

    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependee-tasks."""
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
        """Check if task has no dependents nor dependee-tasks."""
        ...

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        ...


class DependencySubgraphBuilder:
    """Builder for a subgraph of a dependency graph."""

    def __init__(self, graph: IDependencyGraphView) -> None:
        self._graph = graph
        self._minimal_graph_builder = graphs.DirectedGraphBuilder[UID]()

    def add_task(self, task: UID, /) -> None:
        if task not in self._graph.tasks():
            raise TaskDoesNotExistError(task)

        self._minimal_graph_builder.add_node(task)

    def add_dependency(self, dependee_task: UID, dependent_task: UID) -> None:
        if (dependee_task, dependent_task) not in self._graph.dependencies():
            raise DependencyDoesNotExistError(
                dependee_task=dependee_task, dependent_task=dependent_task
            )

        self._minimal_graph_builder.add_edge(
            source=dependee_task, target=dependent_task
        )

    def add_proceeding_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        return self._minimal_graph_builder.add_ancestors_subgraph(
            tasks,
            get_predecessors=self._graph.dependee_tasks,
            stop_condition=stop_condition,
        )

    def add_following_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        return self._minimal_graph_builder.add_descendants_subgraph(
            tasks,
            get_successors=self._graph.dependent_tasks,
            stop_condition=stop_condition,
        )

    def add_connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> set[UID]:
        source_tasks1, source_tasks2 = itertools.tee(source_tasks)
        target_tasks1, target_tasks2 = itertools.tee(target_tasks)

        return self._minimal_graph_builder.add_connecting_subgraph(
            source_tasks1,
            target_tasks1,
            get_successors=self._graph.dependent_tasks,
            get_no_connecting_subgraph_exception=lambda: NoConnectingDependencySubgraphError(
                sources=source_tasks2, targets=target_tasks2
            ),
        )

    def add_component_subgraph(self, task: UID) -> set[UID]:
        return self._minimal_graph_builder.add_component_subgraph(
            task,
            get_successors=self._graph.dependent_tasks,
            get_predecessors=self._graph.dependee_tasks,
        )

    def build(self) -> DependencyGraph:
        return DependencyGraph(self._minimal_graph_builder.build().items())


class DependencyGraph:
    """Graph of task dependencies.

    Shows which tasks have to be completed before another task can be started.

    Acts as a DAG.
    """

    def __init__(
        self, connections: Iterable[tuple[UID, Iterable[UID]]] | None = None
    ) -> None:
        """Initialise DependencyGraph."""
        try:
            self._dag = graphs.DirectedAcyclicGraph[UID](connections=connections)
        except TargetsAreNotNotAlsoSourceNodesError as e:
            raise DependentTasksAreNotAlsoDependeeTasksError(e.targets) from e
        except ConnectionsDictNodesHaveLoops as e:
            raise ConnectionsDictDependencyGraphTasksHaveLoops(e.nodes)
        except ConnectionsDictHasCycleError as e:
            raise ConnectionsDictDependencyGraphHasCycleError(e.dictionary) from e

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        if not isinstance(other, DependencyGraph):
            return NotImplemented

        return (
            self.tasks() == other.tasks()
            and self.dependencies() == other.dependencies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        return str(self._dag)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_dependents = (
            f"{task!r}: {{{', '.join(repr(dependent) for dependent in self.dependent_tasks(task))}}}"
            for task in self.tasks()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_dependents)}}})"

    def clone(self) -> DependencyGraph:
        """Create a clone of the dependency graph."""
        return copy.deepcopy(self)

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
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise DependencyLoopError(e.node) from e
        except graphs.EdgeDoesNotExistError as e:
            if not isinstance(e.source, UID) or not isinstance(e.target, UID):
                raise TypeError from e
            raise DependencyDoesNotExistError(dependee_task, dependent_task) from e

    def tasks(self) -> TasksView:
        """Return a view of the tasks."""
        return TasksView(self._dag.nodes())

    def dependencies(self) -> DependenciesView:
        """Return a view of the dependencies."""
        return DependenciesView(self._dag.edges())

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

    def following_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        builder = DependencySubgraphBuilder(self)
        _ = builder.add_following_subgraph(tasks, stop_condition=stop_condition)
        return builder.build()

    def following_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            yield from self._dag.descendants(tasks, stop_condition=stop_condition)

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def proceeding_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        builder = DependencySubgraphBuilder(self)
        _ = builder.add_proceeding_subgraph(tasks, stop_condition=stop_condition)
        return builder.build()

    def proceeding_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            yield from self._dag.ancestors(tasks, stop_condition=stop_condition)

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        builder = DependencySubgraphBuilder(self)
        _ = builder.add_connecting_subgraph(source_tasks, target_tasks)
        return builder.build()

    def component_subgraph(self, task: UID) -> DependencyGraph:
        builder = DependencySubgraphBuilder(self)
        _ = builder.add_component_subgraph(task)
        return builder.build()

    def component_subgraphs(self) -> Generator[DependencyGraph, None, None]:
        """Yield component subgraphs in the graph."""
        checked_tasks = set[UID]()
        for node in self.tasks():
            if node in checked_tasks:
                continue

            component = self.component_subgraph(node)
            checked_tasks.update(component.tasks())
            yield component

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependee-tasks."""
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
        """Check if task has no dependents nor dependee-tasks."""
        return self._dag.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._dag.isolated_nodes()


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
        return str(self._graph)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_dependents = (
            f"{task!r}: {{{', '.join(repr(dependent) for dependent in self.dependent_tasks(task))}}}"
            for task in self.tasks()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_dependents)}}})"

    def clone(self) -> DependencyGraph:
        """Create a clone of the dependency graph."""
        return self._graph.clone()

    def tasks(self) -> TasksView:
        """Return view of tasks in graph."""
        return self._graph.tasks()

    def dependencies(self) -> DependenciesView:
        """Return view of dependencies in graph."""
        return self._graph.dependencies()

    def dependee_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependee-tasks of a task."""
        return self._graph.dependee_tasks(task)

    def dependent_tasks(self, task: UID, /) -> TasksView:
        """Return a view of the dependent-tasks of a task."""
        return self._graph.dependent_tasks(task)

    def following_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        """Yield following tasks of task, following the specified search order."""
        return self._graph.following_subgraph(tasks, stop_condition=stop_condition)

    def following_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        return self._graph.following_tasks(tasks, stop_condition=stop_condition)

    def proceeding_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> DependencyGraph:
        """Yield proceeding tasks of task, following the specified search order."""
        return self._graph.proceeding_subgraph(tasks, stop_condition=stop_condition)

    def proceeding_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        return self._graph.proceeding_tasks(tasks, stop_condition=stop_condition)

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID]
    ) -> DependencyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph(source_tasks, target_tasks)

    def component_subgraph(self, task: UID) -> DependencyGraph:
        return self._graph.component_subgraph(task)

    def component_subgraphs(self) -> Generator[DependencyGraph, None, None]:
        return self._graph.component_subgraphs()

    def is_first(self, task: UID, /) -> bool:
        """Check if task has no dependee-tasks."""
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
        """Check if task has no dependent-tasks nor dependee-tasks."""
        return self._graph.is_isolated(task)

    def isolated_tasks(self) -> Generator[UID, None, None]:
        """Return generator of isolated tasks."""
        return self._graph.isolated_tasks()
