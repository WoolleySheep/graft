"""Hierarchy Graph and associated classes/exceptions."""

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
from graft.domain.tasks.helpers import (
    TaskDoesNotExistError,
    reraise_node_already_exists_as_task_already_exists,
)
from graft.domain.tasks.uid import (
    UID,
    TasksView,
)
from graft.graphs import (
    ConnectionsDictHasCycleError,
    ConnectionsDictNodesHaveLoops,
    TargetsAreNotNotAlsoSourceNodesError,
    UnderlyingDictHasRedundantEdgesError,
)
from graft.graphs.reduced_directed_acyclic_graph import ReducedDirectedAcyclicGraph

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
        Iterable,
        Iterator,
        Mapping,
    )


class HasHierarchyNeighboursError(Exception):
    """Raised when a task has neighbours.

    A task cannot be removed when it has any neighbours.
    """

    def __init__(
        self,
        task: UID,
        supertasks: Iterable[UID],
        subtasks: Iterable[UID],
    ) -> None:
        self.task = task
        self.supertasks = set(supertasks)
        self.subtasks = set(subtasks)
        formatted_neighbours = (
            str(neighbour)
            for neighbour in itertools.chain(self.supertasks, self.subtasks)
        )
        super().__init__(
            f"Task [{task}] has neighbours [{', '.join(formatted_neighbours)}]"
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


class SubtasksAreNotAlsoSupertasksError(Exception):
    """Raised when some subtasks are not also supertasks."""

    def __init__(
        self,
        subtasks: Iterable[Hashable],
        *args: tuple[Any, ...],
        **kwargs: dict[str, Any],
    ) -> None:
        self.dependent_tasks = set(subtasks)
        super().__init__(
            f"Subtasks [{self.dependent_tasks}] are not also supertasks",
            *args,
            **kwargs,
        )


class ConnectionsDictHierarchyGraphTasksHaveLoops(Exception):
    """Connections used to construct the graph include loops."""

    def __init__(self, tasks: Iterable[Hashable]) -> None:
        self.tasks = set(tasks)
        formatted_tasks = (str(task) for task in self.tasks)
        super().__init__(
            f"Connections used to construct the graph have loops for tasks [{', '.join(formatted_tasks)}]"
        )


class ConnectionsDictHierarchyGraphHasCycleError(Exception):
    """Underlying dictionary has a cycle."""

    def __init__(self, dictionary: Mapping[Any, Set[Any]]) -> None:
        self.dictionary = dict(dictionary)
        super().__init__(f"Underlying dictionary [{dictionary}] has a cycle")


class UnderlyingDictHierarchyGraphHasRedundantEdgesError(Exception):
    """Underlying dictionary has redundant edges."""

    def __init__(self, dictionary: Mapping[Any, Set[Any]]) -> None:
        self.dictionary = dict(dictionary)
        super().__init__(
            f"underlying dictionary [{dictionary}] has redundant dependencies"
        )


def _is_uid_graph(obj: object) -> TypeGuard[ReducedDirectedAcyclicGraph[UID]]:
    return isinstance(obj, ReducedDirectedAcyclicGraph) and all(
        isinstance(item, UID)
        for item in obj.nodes()  # type: ignore
    )


def _reraise_edge_adding_exceptions_as_corresponding_hierarchy_adding_exceptions[
    **P,
    R,
](
    fn: Callable[P, R],
) -> Callable[P, R]:
    """Reraise exceptions raised be validate_edge_can_be_added exceptions as their corresponding validate_hierarchy_can_be_added exceptions."""

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
            raise HierarchyLoopError(e.node) from e
        except graphs.EdgeAlreadyExistsError as e:
            if not isinstance(e.source, UID) or not isinstance(e.target, UID):
                raise TypeError from e
            raise HierarchyAlreadyExistsError(e.source, e.target) from e
        except graphs.IntroducesCycleToReducedGraphError as e:
            if (
                not isinstance(e.source, UID)
                or not isinstance(e.target, UID)
                or not _is_uid_graph(e.connecting_subgraph)
            ):
                raise TypeError from e
            raise HierarchyIntroducesCycleError(
                supertask=e.source,
                subtask=e.target,
                connecting_subgraph=HierarchyGraph(
                    (node, e.connecting_subgraph.successors(node))
                    for node in e.connecting_subgraph.nodes()
                ),
            ) from e
        except graphs.IntroducesRedundantEdgeError as e:
            if (
                not isinstance(e.source, UID)
                or not isinstance(e.target, UID)
                or not _is_uid_graph(e.subgraph)
            ):
                raise TypeError from e
            raise HierarchyIntroducesRedundantHierarchyError(
                supertask=e.source,
                subtask=e.target,
                connecting_subgraph=HierarchyGraph(
                    (node, e.subgraph.successors(node)) for node in e.subgraph.nodes()
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
            raise HasHierarchyNeighboursError(
                task=e.node, supertasks=e.predecessors, subtasks=e.successors
            ) from e

    return wrapper


class HierarchiesView(Set[tuple[UID, UID]]):
    """View of the hierarchies in the graph."""

    def __init__(self, hierarchies: Set[tuple[UID, UID]], /) -> None:
        """Initialise HierarchiesView."""
        self._hierarchies = hierarchies

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
            if not isinstance(e.node, UID):
                raise TypeError from e
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

    def __sub__(self, other: Set[Any]) -> set[tuple[UID, UID]]:
        """Return difference of two views."""
        return set(self._hierarchies - other)

    def __and__(self, other: Set[Any]) -> set[tuple[UID, UID]]:
        """Return intersection of two views."""
        return set(self._hierarchies & other)

    def __or__[G: Hashable](self, other: Set[G]) -> set[tuple[UID, UID] | G]:
        """Return union of two views."""
        return set(self._hierarchies | other)

    def __xor__[G: Hashable](self, other: Set[G]) -> set[tuple[UID, UID] | G]:
        """Return symmetric difference of two views."""
        return set(self._hierarchies ^ other)

    def __le__(self, other: Set[Any]) -> bool:
        """Subset test (self <= other)."""
        return self._hierarchies <= other

    def __lt__(self, other: Set[Any]) -> bool:
        """Proper subset test (self < other)."""
        return self._hierarchies < other

    def __ge__(self, other: Set[Any]) -> bool:
        """Superset test (self >= other)."""
        return self._hierarchies >= other

    def __gt__(self, other: Set[Any]) -> bool:
        """Proper superset test (self > other)."""
        return self._hierarchies > other


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

    def clone(self) -> HierarchyGraph:
        """Create a clone of the hierarchy graph."""
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

    def inferior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph: ...

    def inferior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]: ...

    def superior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph: ...

    def superior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]: ...

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between the source and target task."""
        ...

    def component_subgraph(self, task: UID) -> HierarchyGraph: ...

    def component_subgraphs(self) -> Generator[HierarchyGraph, None, None]: ...

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


class HierarchySubgraphBuilder:
    """Builder for a subgraph of a hierarchy graph."""

    def __init__(self, graph: IHierarchyGraphView) -> None:
        self._graph = graph
        self._minimal_graph_builder = graphs.DirectedGraphBuilder[UID]()

    def add_task(self, task: UID, /) -> None:
        if task not in self._graph.tasks():
            raise TaskDoesNotExistError(task)

        self._minimal_graph_builder.add_node(task)

    def add_hierarchy(self, supertask: UID, subtask: UID) -> None:
        if (supertask, subtask) not in self._graph.hierarchies():
            raise HierarchyDoesNotExistError(supertask=supertask, subtask=subtask)

        self._minimal_graph_builder.add_edge(source=supertask, target=subtask)

    def add_superior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        return self._minimal_graph_builder.add_ancestors_subgraph(
            tasks,
            get_predecessors=self._graph.supertasks,
            stop_condition=stop_condition,
        )

    def add_inferior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> set[UID]:
        return self._minimal_graph_builder.add_descendants_subgraph(
            tasks,
            get_successors=self._graph.subtasks,
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
            get_successors=self._graph.subtasks,
            get_no_connecting_subgraph_exception=lambda: NoConnectingHierarchySubgraphError(
                sources=source_tasks2, targets=target_tasks2
            ),
        )

    def add_component_subgraph(self, task: UID) -> set[UID]:
        return self._minimal_graph_builder.add_component_subgraph(
            task,
            get_successors=self._graph.subtasks,
            get_predecessors=self._graph.supertasks,
        )

    def build(self) -> HierarchyGraph:
        return HierarchyGraph(self._minimal_graph_builder.build().items())


class HierarchyGraph:
    """Graph of task hierarchies.

    Shows which tasks are subtasks of other tasks.

    Acts as a Minimum DAG.
    """

    def __init__(
        self, connections: Iterable[tuple[UID, Iterable[UID]]] | None = None
    ) -> None:
        """Initialise HierarchyGraph."""
        try:
            self._reduced_dag = graphs.ReducedDirectedAcyclicGraph[UID](
                connections=connections
            )
        except TargetsAreNotNotAlsoSourceNodesError as e:
            raise SubtasksAreNotAlsoSupertasksError(e.targets) from e
        except ConnectionsDictNodesHaveLoops as e:
            raise ConnectionsDictHierarchyGraphTasksHaveLoops(e.nodes)
        except ConnectionsDictHasCycleError as e:
            raise ConnectionsDictHierarchyGraphHasCycleError(e.dictionary) from e
        except UnderlyingDictHasRedundantEdgesError as e:
            raise UnderlyingDictHierarchyGraphHasRedundantEdgesError(
                e.dictionary
            ) from e

    def __bool__(self) -> bool:
        """Check if graph is not empty."""
        return bool(self._reduced_dag)

    def __eq__(self, other: object) -> bool:
        """Check if two graphs are equal."""
        if not isinstance(other, HierarchyGraph):
            return NotImplemented

        return (
            self.tasks() == other.tasks() and self.hierarchies() == other.hierarchies()
        )

    def __str__(self) -> str:
        """Return string representation of graph."""
        return str(self._reduced_dag)

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = (
            f"{task!r}: {{{', '.join(repr(subtask) for subtask in self.subtasks(task))}}}"
            for task in self.tasks()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_subtasks)}}})"

    def clone(self) -> HierarchyGraph:
        """Create a clone of the hierarchy graph."""
        return copy.deepcopy(self)

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

    def inferior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        builder = HierarchySubgraphBuilder(self)
        _ = builder.add_inferior_subgraph(tasks, stop_condition=stop_condition)
        return builder.build()

    def inferior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            yield from self._reduced_dag.descendants(
                tasks, stop_condition=stop_condition
            )

    @helpers.reraise_node_does_not_exist_as_task_does_not_exist()
    def superior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        builder = HierarchySubgraphBuilder(self)
        _ = builder.add_superior_subgraph(tasks, stop_condition=stop_condition)
        return builder.build()

    def superior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        with helpers.reraise_node_does_not_exist_as_task_does_not_exist():
            yield from self._reduced_dag.ancestors(tasks, stop_condition=stop_condition)

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        builder = HierarchySubgraphBuilder(self)
        _ = builder.add_connecting_subgraph(source_tasks, target_tasks)
        return builder.build()

    def component_subgraph(self, task: UID) -> HierarchyGraph:
        builder = HierarchySubgraphBuilder(self)
        _ = builder.add_component_subgraph(task)
        return builder.build()

    def component_subgraphs(self) -> Generator[HierarchyGraph, None, None]:
        """Yield component subgraphs in the graph."""
        checked_tasks = set[UID]()
        for node in self.tasks():
            if node in checked_tasks:
                continue

            component = self.component_subgraph(node)
            checked_tasks.update(component.tasks())
            yield component

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
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise TaskDoesNotExistError(e.node) from e
        except graphs.LoopError as e:
            if not isinstance(e.node, UID):
                raise TypeError from e
            raise HierarchyLoopError(supertask) from e
        except graphs.EdgeDoesNotExistError as e:
            if not isinstance(e.source, UID) or not isinstance(e.target, UID):
                raise TypeError from e
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
            f"{task}: {{{', '.join(str(subtask) for subtask in self.subtasks(task))}}}"
            for task in self.tasks()
        )
        return f"{{{', '.join(tasks_with_subtasks)}}}"

    def __repr__(self) -> str:
        """Return string representation of graph."""
        tasks_with_subtasks = (
            f"{task!r}: {{{', '.join(repr(subtask) for subtask in self.subtasks(task))}}}"
            for task in self.tasks()
        )
        return f"{self.__class__.__name__}({{{', '.join(tasks_with_subtasks)}}})"

    def clone(self) -> HierarchyGraph:
        """Create a clone of the hierarchy graph."""
        return self._graph.clone()

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

    def inferior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        return self._graph.inferior_subgraph(tasks, stop_condition=stop_condition)

    def inferior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        return self._graph.inferior_tasks(tasks, stop_condition=stop_condition)

    def superior_subgraph(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> HierarchyGraph:
        return self._graph.superior_subgraph(tasks, stop_condition=stop_condition)

    def superior_tasks(
        self,
        tasks: Iterable[UID],
        /,
        stop_condition: Callable[[UID], bool] | None = None,
    ) -> Generator[UID, None, None]:
        return self._graph.superior_tasks(tasks, stop_condition=stop_condition)

    def connecting_subgraph(
        self, source_tasks: Iterable[UID], target_tasks: Iterable[UID], /
    ) -> HierarchyGraph:
        """Return subgraph of tasks between source and target tasks."""
        return self._graph.connecting_subgraph(source_tasks, target_tasks)

    def component_subgraph(self, task: UID) -> HierarchyGraph:
        return self._graph.component_subgraph(task)

    def component_subgraphs(self) -> Generator[HierarchyGraph, None, None]:
        return self._graph.component_subgraphs()

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
