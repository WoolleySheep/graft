import collections
import itertools
import statistics
from collections.abc import (
    Callable,
    Collection,
    Generator,
    Iterable,
    Mapping,
    MutableMapping,
    Set,
    Sized,
)
from typing import Final, Hashable

from graft import graphs
from graft.domain import tasks
from graft.domain.tasks.dependency_graph import IDependencyGraphView
from graft.domain.tasks.hierarchy_graph import IHierarchyGraphView
from graft.domain.tasks.network_graph import INetworkGraphView, NetworkGraph
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.position import (
    RelationPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)

NUMBER_OF_HIERARCHY_LAYER_DEPTH_INDEX_ITERATIONS: Final = 20
NUMBER_OF_DEPTH_POSITION_ITERATIONS: Final = 20


class DummyUID(tasks.UID):
    """UID of task introduced to ensure single-level hierarchies."""


class DummyTaskRelationPosition:
    """The position of the dummy task cylinder resulting from its hierarchy and dependency relationships."""

    def __init__(
        self,
        dependency_position: float,
        hierarchy_position: int,
    ) -> None:
        self._dependency = dependency_position
        self._hierarchy = hierarchy_position

    @property
    def dependency(self) -> float:
        return self._dependency

    @property
    def hierarchy(self) -> int:
        return self._hierarchy


def get_depth_positions_cascade_method(
    graph: tasks.INetworkGraphView,
    relation_positions: Mapping[tasks.UID, RelationPosition],
    task_cylinder_radius: Radius,
) -> dict[tasks.UID, float]:
    return {
        task: 3 * float(task_cylinder_radius) * task_number
        for task_number, task in enumerate(relation_positions)
    }


def _generate_graph_with_dummy_tasks(
    graph: tasks.INetworkGraphView,
    relation_positions: Mapping[tasks.UID, RelationPosition],
) -> tuple[tasks.NetworkGraph, dict[DummyUID, DummyTaskRelationPosition]]:
    """Create a clone of the graph with dummy tasks.

    Dummy tasks are added to ensure that a hierarchy only stretches across one
    level; hierarchies that stretched across multiple levels are broken into a
    number of smaller hierarchies, with dummy tasks on the intervening levels.

    Dummy tasks have a dependency min/max position equivalent to the midpoint of
    the subtask whose hierarchy they're modifying. This means that they can have
    dependency positions at multiples of 0.5, as opposed to the multiples of 1
    (aka: integers) allowed for normal task dependency positions.

    My current dummy UID implementation isn't particularly type safe, and
    requires on nobody using the DummyUID class outside this context &
    nobody having over 10000 tasks. find a better way.
    """
    graph_with_dummies = tasks.NetworkGraph.clone(graph)
    relation_positions_with_dummies = dict[DummyUID, DummyTaskRelationPosition]()

    dummy_task_counter = 10000
    for supertask, subtask in list(graph.hierarchy_graph().hierarchies()):
        if (
            relation_positions[supertask].hierarchy
            - relation_positions[subtask].hierarchy
        ) == 1:
            # Only a single-level hierarchy; nothing to do here
            continue

        graph_with_dummies.remove_hierarchy(supertask, subtask)
        dummy_tasks_replacing_current_hierarchy = list[DummyUID]()

        dependency_position = (
            relation_positions[subtask].dependency.min
            + relation_positions[subtask].dependency.max
        ) / 2

        for dummy_task_hierarchy_position in range(
            relation_positions[supertask].hierarchy - 1,
            relation_positions[subtask].hierarchy,
            -1,
        ):
            dummy_task = DummyUID(dummy_task_counter)
            dummy_task_counter += 1
            dummy_tasks_replacing_current_hierarchy.append(dummy_task)
            graph_with_dummies.add_task(dummy_task)

            dummy_task_position = DummyTaskRelationPosition(
                dependency_position, dummy_task_hierarchy_position
            )
            relation_positions_with_dummies[dummy_task] = dummy_task_position

        tasks_in_hierarchy_chain = itertools.chain(
            [supertask], dummy_tasks_replacing_current_hierarchy, [subtask]
        )

        for dummy_supertask, dummy_subtask in itertools.pairwise(
            tasks_in_hierarchy_chain
        ):
            graph_with_dummies.add_hierarchy(dummy_supertask, dummy_subtask)

    return graph_with_dummies, relation_positions_with_dummies


def _get_task_hierarchy_layers(
    hierarchy_graph: IHierarchyGraphView,
) -> list[set[tasks.UID]]:
    """Get the hierarchy layers of the graph, in order of increasing hierarchy depth."""
    graph = graph_conversion.convert_hierarchy_to_reduced_dag(hierarchy_graph)
    return list(graph.topologically_sorted_groups())


def _calculate_median_of_neighbours[T: Hashable](
    node: T,
    get_neighbours: Callable[[T], Iterable[T]],
    node_to_value_map: Mapping[T, float],
) -> float:
    return statistics.median(
        node_to_value_map[neighbour] for neighbour in get_neighbours(node)
    )


def _calculate_median_index_of_supertasks(
    task: tasks.UID,
    graph: IHierarchyGraphView,
    task_to_index_map: Mapping[tasks.UID, int],
) -> float:
    return _calculate_median_of_neighbours(
        node=task, get_neighbours=graph.supertasks, node_to_value_map=task_to_index_map
    )


def _calculate_median_index_of_subtasks(
    task: tasks.UID,
    graph: IHierarchyGraphView,
    task_to_index_map: Mapping[tasks.UID, int],
) -> float:
    return _calculate_median_of_neighbours(
        node=task, get_neighbours=graph.subtasks, node_to_value_map=task_to_index_map
    )


def _get_groups_along_dependency_axis(
    tasks_to_assess: Collection[tasks.UID],  # TODO: Shit name, think of a better one
    relation_positions: Mapping[tasks.UID, RelationPosition],
    relation_positions_of_dummy_tasks: Mapping[DummyUID, DummyTaskRelationPosition],
) -> Generator[set[tasks.UID], None, None]:
    # For example A starts at 1 & ends at 3, B starts at 2 & ends at 2, C starts at 2 & ends at 4.
    # Groups would be: {A}, # {A, B, C}, {A, C}
    min_scaled_dependency_position_to_task_map = collections.defaultdict[
        int, set[tasks.UID]
    ](set)
    max_scaled_dependency_position_to_task_map = collections.defaultdict[
        int, set[tasks.UID]
    ](set)
    for task in tasks_to_assess:
        if isinstance(task, DummyUID):
            min_dependency_position = relation_positions_of_dummy_tasks[task].dependency
            max_dependency_position = relation_positions_of_dummy_tasks[task].dependency
        else:
            min_dependency_position = relation_positions[task].dependency.min
            max_dependency_position = relation_positions[task].dependency.max

        min_scaled_dependency_position = round(2 * min_dependency_position)
        max_scaled_dependency_position = round(2 * max_dependency_position)

        min_scaled_dependency_position_to_task_map[min_scaled_dependency_position].add(
            task
        )
        max_scaled_dependency_position_to_task_map[max_scaled_dependency_position].add(
            task
        )

    sorted_min_scaled_dependency_position_groups = collections.deque(
        sorted(min_scaled_dependency_position_to_task_map.items())
    )

    sorted_max_scaled_dependency_position_groups = collections.deque(
        sorted(max_scaled_dependency_position_to_task_map.items())
    )

    previous_position_task_group = set[tasks.UID]()

    while sorted_min_scaled_dependency_position_groups:
        (
            dependency_position,
            tasks_starting,
        ) = sorted_min_scaled_dependency_position_groups.popleft()

        task_group = previous_position_task_group | tasks_starting

        while sorted_max_scaled_dependency_position_groups[0][0] < dependency_position:
            (
                _,
                tasks_ended,
            ) = sorted_max_scaled_dependency_position_groups.popleft()
            for task in tasks_ended:
                task_group.remove(task)

        yield task_group

        previous_position_task_group = task_group


def _construct_depth_graph(
    task_groups_along_dependency_axis: Iterable[Set[tasks.UID]],
    task_to_median_index_of_neighbours_map: Mapping[tasks.UID, float],
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    depth_graph = graphs.DirectedAcyclicGraph[tasks.UID]()

    for task_group in task_groups_along_dependency_axis:
        for task in task_group:
            if task in depth_graph.nodes():
                continue
            depth_graph.add_node(task)

        task_group_sorted_by_median_index = sorted(
            task_group, key=lambda task: task_to_median_index_of_neighbours_map[task]
        )

        for task1, task2 in itertools.pairwise(task_group_sorted_by_median_index):
            # No point adding an edge if it's already there, and we don't want to introduce any cycles
            if (task1, task2) in depth_graph.edges() or depth_graph.has_path(
                task2, task1
            ):
                continue

            depth_graph.add_edge(task1, task2)

    return depth_graph


def _get_topological_sort_group_indexes[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> dict[T, int]:
    task_to_topological_sort_group_index_map = dict[T, int]()
    for index, group in enumerate(graph.topologically_sorted_groups()):
        for task in group:
            task_to_topological_sort_group_index_map[task] = index

    return task_to_topological_sort_group_index_map


def _get_depth_indexes_unamed_method(
    graph: NetworkGraph,
    relation_positions: Mapping[tasks.UID, RelationPosition],
    relation_positions_of_dummy_tasks: Mapping[DummyUID, DummyTaskRelationPosition],
) -> dict[tasks.UID, int]:
    hierarchy_layers = _get_task_hierarchy_layers(graph.hierarchy_graph())

    hierarchy_layers_with_dependency_groups = [
        (
            layer,
            list(
                _get_groups_along_dependency_axis(
                    layer, relation_positions, relation_positions_of_dummy_tasks
                )
            ),
        )
        for layer in hierarchy_layers
    ]

    # Populate initial task indexes
    task_to_depth_index_map = dict[tasks.UID, int]()
    for layer in hierarchy_layers:
        for index, task in enumerate(layer):
            task_to_depth_index_map[task] = index

    for _ in range(NUMBER_OF_HIERARCHY_LAYER_DEPTH_INDEX_ITERATIONS):
        for layer, dependency_groups in itertools.islice(
            hierarchy_layers_with_dependency_groups, 1, None
        ):
            task_to_median_index_of_supertasks_map = {
                task: _calculate_median_index_of_supertasks(
                    task, graph.hierarchy_graph(), task_to_depth_index_map
                )
                if graph.hierarchy_graph().supertasks(task)
                else layer_index
                for layer_index, task in enumerate(layer)
            }

            depth_graph = _construct_depth_graph(
                dependency_groups, task_to_median_index_of_supertasks_map
            )

            layer_task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

            for task, depth_index in layer_task_to_depth_index_map.items():
                task_to_depth_index_map[task] = depth_index

        for layer, dependency_groups in itertools.islice(
            reversed(hierarchy_layers_with_dependency_groups), 1, None
        ):
            task_to_median_index_of_subtasks_map = {
                task: _calculate_median_index_of_subtasks(
                    task, graph.hierarchy_graph(), task_to_depth_index_map
                )
                if graph.hierarchy_graph().subtasks(task)
                else layer_index
                for layer_index, task in enumerate(layer)
            }

            depth_graph = _construct_depth_graph(
                dependency_groups, task_to_median_index_of_subtasks_map
            )

            layer_task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

            for task, depth_index in layer_task_to_depth_index_map.items():
                task_to_depth_index_map[task] = depth_index

        for layer, dependency_groups in itertools.islice(
            hierarchy_layers_with_dependency_groups, 1, None
        ):
            task_to_median_index_of_supertasks_map = {
                task: _calculate_median_index_of_supertasks(
                    task, graph.hierarchy_graph(), task_to_depth_index_map
                )
                if graph.hierarchy_graph().supertasks(task)
                else layer_index
                for layer_index, task in enumerate(layer)
            }

            depth_graph = _construct_depth_graph(
                reversed(dependency_groups), task_to_median_index_of_supertasks_map
            )

            layer_task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

            for task, depth_index in layer_task_to_depth_index_map.items():
                task_to_depth_index_map[task] = depth_index

        for layer, dependency_groups in itertools.islice(
            reversed(hierarchy_layers_with_dependency_groups), 1, None
        ):
            task_to_median_index_of_subtasks_map = {
                task: _calculate_median_index_of_subtasks(
                    task, graph.hierarchy_graph(), task_to_depth_index_map
                )
                if graph.hierarchy_graph().subtasks(task)
                else layer_index
                for layer_index, task in enumerate(layer)
            }

            depth_graph = _construct_depth_graph(
                reversed(dependency_groups), task_to_median_index_of_subtasks_map
            )

            layer_task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

            for task, depth_index in layer_task_to_depth_index_map.items():
                task_to_depth_index_map[task] = depth_index

    return task_to_depth_index_map


class Priority:
    """Priority of a task for movement purposes.

    Having no priority set is the highest priority of all.
    """

    def __init__(self, n: int | None = None) -> None:
        self.n = n

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise NotImplementedError

        return other.n is None or (self.n is not None and self.n < other.n)


def _get_average_of_neighbour_values[T: Hashable](
    node: T,
    get_neighbours: Callable[[T], Collection[T]],
    node_to_value_map: Mapping[T, float],
) -> float:
    neighbours = get_neighbours(node)
    return sum(node_to_value_map[neighbour] for neighbour in neighbours) / len(
        neighbours
    )


def _get_average_position_of_supertasks(
    task: tasks.UID,
    graph: IHierarchyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.supertasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_position_of_subtasks(
    task: tasks.UID,
    graph: IHierarchyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.subtasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_position_of_dependee_tasks(
    task: tasks.UID,
    graph: IDependencyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.dependee_tasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_position_of_dependent_tasks(
    task: tasks.UID,
    graph: IDependencyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.dependent_tasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_neighbours_priority(
    task: tasks.UID, get_neighbours: Callable[[tasks.UID], Sized]
) -> Priority:
    if isinstance(task, DummyUID):
        return Priority()

    number_of_neighbours = len(get_neighbours(task))
    return Priority(number_of_neighbours)


def _get_supertasks_priority(task: tasks.UID, graph: IHierarchyGraphView) -> Priority:
    return _get_neighbours_priority(task=task, get_neighbours=graph.supertasks)


def _get_subtasks_priority(task: tasks.UID, graph: IHierarchyGraphView) -> Priority:
    return _get_neighbours_priority(task=task, get_neighbours=graph.subtasks)


def _get_dependee_tasks_priority(
    task: tasks.UID, graph: IDependencyGraphView
) -> Priority:
    return _get_neighbours_priority(task=task, get_neighbours=graph.dependee_tasks)


def _get_dependent_tasks_priority(
    task: tasks.UID, graph: IDependencyGraphView
) -> Priority:
    return _get_neighbours_priority(task=task, get_neighbours=graph.dependent_tasks)


def _get_simple_depth_graph(
    task_groups_along_dependency_axis: Iterable[Iterable[tasks.UID]],
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    depth_graph = graphs.DirectedAcyclicGraph[tasks.UID]()
    for task_group in task_groups_along_dependency_axis:
        for task in task_group:
            if task in depth_graph.nodes():
                continue
            depth_graph.add_node(task)

        for task1, task2 in itertools.pairwise(task_group):
            # No point adding an edge if it's already there
            if (task1, task2) in depth_graph.edges():
                continue

            depth_graph.add_edge(task1, task2)

    return depth_graph


def _move_task(
    task: tasks.UID,
    ideal_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    current_position = task_to_depth_position_map[task]

    if current_position < ideal_position:
        _shift_task_deeper(
            task=task,
            threshold_position=ideal_position,
            layer_depth_graph=layer_depth_graph,
            task_to_depth_position_map=task_to_depth_position_map,
            task_to_priority_map=task_to_priority_map,
            min_separation_distance=min_separation_distance,
        )
    elif current_position > ideal_position:
        _shift_task_shallower(
            task=task,
            threshold_position=ideal_position,
            layer_depth_graph=layer_depth_graph,
            task_to_depth_position_map=task_to_depth_position_map,
            task_to_priority_map=task_to_priority_map,
            min_separation_distance=min_separation_distance,
        )


def _shift_task_deeper(
    task: tasks.UID,
    threshold_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    # Task is the deepest task - base case
    if layer_depth_graph.is_root(task):
        task_to_depth_position_map[task] = max(
            task_to_depth_position_map[task], threshold_position
        )
        return

    for deeper_task in layer_depth_graph.successors(task):
        if task_to_priority_map[deeper_task] < task_to_priority_map[task]:
            _shift_task_deeper(
                task=deeper_task,
                threshold_position=threshold_position + min_separation_distance,
                layer_depth_graph=layer_depth_graph,
                task_to_depth_position_map=task_to_depth_position_map,
                task_to_priority_map=task_to_priority_map,
                min_separation_distance=min_separation_distance,
            )

    deeper_task_positions = (
        task_to_depth_position_map[deeper_task]
        for deeper_task in layer_depth_graph.successors(task)
    )
    task_to_depth_position_map[task] = min(
        itertools.chain(
            [threshold_position],
            (
                deeper_task_position - min_separation_distance
                for deeper_task_position in deeper_task_positions
            ),
        )
    )


def _shift_task_shallower(
    task: tasks.UID,
    threshold_position: float,
    layer_depth_graph: graphs.DirectedAcyclicGraph[tasks.UID],
    task_to_depth_position_map: MutableMapping[tasks.UID, float],
    task_to_priority_map: Mapping[tasks.UID, Priority],
    min_separation_distance: float,
) -> None:
    # Task is the shallowest task - base case
    if layer_depth_graph.is_root(task):
        task_to_depth_position_map[task] = min(
            task_to_depth_position_map[task], threshold_position
        )
        return

    for shallower_task in layer_depth_graph.predecessors(task):
        if task_to_priority_map[shallower_task] < task_to_priority_map[task]:
            _shift_task_shallower(
                task=shallower_task,
                threshold_position=threshold_position - min_separation_distance,
                layer_depth_graph=layer_depth_graph,
                task_to_depth_position_map=task_to_depth_position_map,
                task_to_priority_map=task_to_priority_map,
                min_separation_distance=min_separation_distance,
            )

    shallower_task_positions = (
        task_to_depth_position_map[shallower_task]
        for shallower_task in layer_depth_graph.predecessors(task)
    )
    task_to_depth_position_map[task] = max(
        itertools.chain(
            [threshold_position],
            (
                shallower_task_position + min_separation_distance
                for shallower_task_position in shallower_task_positions
            ),
        )
    )


def _get_depth_positions_priority_method(
    graph: INetworkGraphView,
    relation_positions: Mapping[tasks.UID, RelationPosition],
    relation_positions_of_dummy_tasks: Mapping[DummyUID, DummyTaskRelationPosition],
    task_to_depth_index_map: Mapping[tasks.UID, int],
    starting_separation_distance: float,
    min_separation_distance: float,
) -> dict[tasks.UID, float]:
    if starting_separation_distance <= 0:
        raise ValueError

    if min_separation_distance <= 0:
        raise ValueError

    # Tasks in layers sorted
    layers_sorted_by_depth_index = [
        sorted(layer, key=lambda task: task_to_depth_index_map[task])
        for layer in _get_task_hierarchy_layers(graph.hierarchy_graph())
    ]

    depth_graphs = [
        _get_simple_depth_graph(
            _get_groups_along_dependency_axis(
                layer, relation_positions, relation_positions_of_dummy_tasks
            )
        )
        for layer in layers_sorted_by_depth_index
    ]

    task_to_depth_graph_map = dict[tasks.UID, graphs.DirectedAcyclicGraph[tasks.UID]]()
    for layer, depth_graph in zip(layers_sorted_by_depth_index, depth_graphs):
        for task in layer:
            task_to_depth_graph_map[task] = depth_graph

    groups_along_dependency_axis = list(
        _get_groups_along_dependency_axis(
            graph.tasks(),
            relation_positions=relation_positions,
            relation_positions_of_dummy_tasks=relation_positions_of_dummy_tasks,
        )
    )

    # Populate initial depth positions
    task_to_depth_position_map = {
        task: starting_separation_distance * depth_index
        for task, depth_index in task_to_depth_index_map.items()
    }

    task_to_supertask_priority_map = {
        task: _get_supertasks_priority(task, graph.hierarchy_graph())
        for task in graph.tasks()
    }
    layers_sorted_by_descending_subtask_priority = [
        sorted(
            layer, key=lambda task: task_to_supertask_priority_map[task], reverse=True
        )
        for layer in layers_sorted_by_depth_index
    ]

    task_to_subtask_priority_map = {
        task: _get_subtasks_priority(task, graph.hierarchy_graph())
        for task in graph.tasks()
    }
    layers_sorted_by_descending_subtask_priority = [
        sorted(layer, key=lambda task: task_to_subtask_priority_map[task], reverse=True)
        for layer in layers_sorted_by_depth_index
    ]

    task_to_dependee_task_priority_map = {
        task: _get_dependee_tasks_priority(task, graph.dependency_graph())
        for task in graph.tasks()
    }
    groups_along_dependency_axis_sorted_by_descending_dependee_task_priority = [
        sorted(
            group,
            key=lambda task: task_to_dependee_task_priority_map[task],
            reverse=True,
        )
        for group in groups_along_dependency_axis
    ]

    task_to_dependent_task_priority_map = {
        task: _get_dependent_tasks_priority(task, graph.dependency_graph())
        for task in graph.tasks()
    }
    groups_along_dependency_axis_sorted_by_descending_dependent_task_priority = [
        sorted(
            group,
            key=lambda task: task_to_dependent_task_priority_map[task],
            reverse=True,
        )
        for group in groups_along_dependency_axis
    ]

    for _ in range(NUMBER_OF_DEPTH_POSITION_ITERATIONS):
        for (
            layer_sorted_by_descending_subtask_priority,
            depth_graph,
        ) in itertools.islice(
            zip(layers_sorted_by_descending_subtask_priority, depth_graphs), 1, None
        ):
            for task in layer_sorted_by_descending_subtask_priority:
                ideal_position = _get_average_position_of_supertasks(
                    task=task,
                    graph=graph.hierarchy_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_supertask_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for (
            layer_sorted_by_descending_subtask_priority,
            depth_graph,
        ) in itertools.islice(
            reversed(
                list(zip(layers_sorted_by_descending_subtask_priority, depth_graphs))
            ),
            1,
            None,
        ):
            for task in layer_sorted_by_descending_subtask_priority:
                # Some tasks don't have subtasks - no need to move these
                if not graph.hierarchy_graph().subtasks(task):
                    continue

                ideal_position = _get_average_position_of_subtasks(
                    task=task,
                    graph=graph.hierarchy_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_subtask_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for group_sorted_by_descending_dependee_task_priority in itertools.islice(
            groups_along_dependency_axis_sorted_by_descending_dependee_task_priority,
            1,
            None,
        ):
            for task in group_sorted_by_descending_dependee_task_priority:
                if not graph.dependency_graph().dependee_tasks(task):
                    continue

                ideal_position = _get_average_position_of_dependee_tasks(
                    task=task,
                    graph=graph.dependency_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=task_to_depth_graph_map[task],
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_dependee_task_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for group_sorted_by_descending_dependent_task_priority in itertools.islice(
            reversed(
                groups_along_dependency_axis_sorted_by_descending_dependent_task_priority
            ),
            1,
            None,
        ):
            for task in group_sorted_by_descending_dependent_task_priority:
                if not graph.dependency_graph().dependent_tasks(task):
                    continue

                ideal_position = _get_average_position_of_dependent_tasks(
                    task=task,
                    graph=graph.dependency_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=task_to_depth_graph_map[task],
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_dependent_task_priority_map,
                    min_separation_distance=min_separation_distance,
                )

    return task_to_depth_position_map


def get_depth_positions_unnamed_method(
    graph: tasks.INetworkGraphView,
    relation_positions: Mapping[tasks.UID, RelationPosition],
    task_cylinder_radius: Radius,
) -> dict[tasks.UID, float]:
    # Add dummy tasks to graph and relation positions
    (
        graph_with_dummies,
        relation_positions_of_dummy_tasks,
    ) = _generate_graph_with_dummy_tasks(graph, relation_positions)

    task_to_depth_index_map = _get_depth_indexes_unamed_method(
        graph_with_dummies, relation_positions, relation_positions_of_dummy_tasks
    )

    return _get_depth_positions_priority_method(
        graph=graph,
        relation_positions=relation_positions,
        relation_positions_of_dummy_tasks=relation_positions_of_dummy_tasks,
        task_to_depth_index_map=task_to_depth_index_map,
        # TODO: These separation values were pulled out of thin air - more investigation required
        starting_separation_distance=16 * float(task_cylinder_radius),
        min_separation_distance=12 * float(task_cylinder_radius),
    )
