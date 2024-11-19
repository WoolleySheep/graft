import itertools
from collections.abc import (
    Callable,
    Collection,
    Hashable,
    Mapping,
    MutableMapping,
    Sequence,
)
from typing import Final

from graft import graphs
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.dependency_axis_grouping import (
    get_dependency_axis_groups,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_graph import (
    get_constrained_depth_graph,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.dummy_tasks import (
    DummyUID,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
    get_hierarchy_layers_in_descending_order,
)

NUMBER_OF_DEPTH_POSITION_ITERATIONS: Final = 20


class Priority:
    """Priority of a task for movement purposes.

    Having no priority set is the highest priority of all.
    """

    def __init__(self, n: int | None = None) -> None:
        self.n = n

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Priority) and self.n == other.n

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Priority):
            raise NotImplementedError

        return self.n is not None and (other.n is None or self.n < other.n)


def _get_average_of_neighbour_values[T: Hashable](
    node: T,
    get_neighbours: Callable[[T], Collection[T]],
    node_to_value_map: Mapping[T, float],
) -> float:
    neighbours = get_neighbours(node)
    return sum(node_to_value_map[neighbour] for neighbour in neighbours) / len(
        neighbours
    )


def _get_average_depth_position_of_supertasks(
    task: tasks.UID,
    graph: tasks.IHierarchyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.supertasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_depth_position_of_subtasks(
    task: tasks.UID,
    graph: tasks.IHierarchyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.subtasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_depth_position_of_dependee_tasks(
    task: tasks.UID,
    graph: tasks.IDependencyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.dependee_tasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_average_depth_position_of_dependent_tasks(
    task: tasks.UID,
    graph: tasks.IDependencyGraphView,
    task_to_depth_position_map: Mapping[tasks.UID, float],
) -> float:
    return _get_average_of_neighbour_values(
        node=task,
        get_neighbours=graph.dependent_tasks,
        node_to_value_map=task_to_depth_position_map,
    )


def _get_neighbours_priority(
    task: tasks.UID, get_number_of_neighbours: Callable[[tasks.UID], int]
) -> Priority:
    return (
        Priority()
        if isinstance(task, DummyUID)
        else Priority(get_number_of_neighbours(task))
    )


def _get_supertasks_priority(
    task: tasks.UID, graph: tasks.IHierarchyGraphView
) -> Priority:
    return _get_neighbours_priority(
        task=task, get_number_of_neighbours=lambda task: len(graph.supertasks(task))
    )


def _get_subtasks_priority(
    task: tasks.UID, graph: tasks.IHierarchyGraphView
) -> Priority:
    return _get_neighbours_priority(
        task=task, get_number_of_neighbours=lambda task: len(graph.subtasks(task))
    )


def _get_dependee_tasks_priority(
    task: tasks.UID, graph: tasks.IDependencyGraphView
) -> Priority:
    return _get_neighbours_priority(
        task=task, get_number_of_neighbours=lambda task: len(graph.dependee_tasks(task))
    )


def _get_dependent_tasks_priority(
    task: tasks.UID, graph: tasks.IDependencyGraphView
) -> Priority:
    return _get_neighbours_priority(
        task=task,
        get_number_of_neighbours=lambda task: len(graph.dependent_tasks(task)),
    )


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


class HierarchyLayer:
    def __init__(
        self,
        tasks_with_supertasks_sorted_by_descending_supertask_priority: Sequence[
            tasks.UID
        ],
        tasks_with_subtasks_sorted_by_descending_subtask_priority: Sequence[tasks.UID],
    ) -> None:
        self.tasks_with_supertasks_sorted_by_descending_supertask_priority = (
            tasks_with_supertasks_sorted_by_descending_supertask_priority
        )
        self.tasks_with_subtasks_sorted_by_descending_subtask_priority = (
            tasks_with_subtasks_sorted_by_descending_subtask_priority
        )


class DependencyLayer:
    def __init__(
        self,
        tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority: Sequence[
            tasks.UID
        ],
        tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority: Sequence[
            tasks.UID
        ],
    ) -> None:
        self.tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority = (
            tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority
        )
        self.tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority = (
            tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority
        )


def get_depth_positions_priority_method(
    graph: tasks.INetworkGraphView,
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
    task_to_depth_index_map: Mapping[tasks.UID, int],
    starting_separation_distance: float,
    min_separation_distance: float,
) -> dict[tasks.UID, float]:
    if starting_separation_distance <= 0:
        raise ValueError

    if min_separation_distance <= 0:
        raise ValueError

    task_to_supertask_priority_map = {
        task: _get_supertasks_priority(task, graph.hierarchy_graph())
        for task in graph.tasks()
    }

    task_to_subtask_priority_map = {
        task: _get_subtasks_priority(task, graph.hierarchy_graph())
        for task in graph.tasks()
    }

    task_to_depth_graph_map = dict[tasks.UID, graphs.DirectedAcyclicGraph[tasks.UID]]()
    hierarchy_layers = list[HierarchyLayer]()
    for layer in get_hierarchy_layers_in_descending_order(task_to_relation_layers_map):
        dependency_axis_groups = get_dependency_axis_groups(
            tasks_=layer, task_to_relation_layers_map=task_to_relation_layers_map
        )
        depth_graph = get_constrained_depth_graph(
            dependency_axis_groups, task_to_depth_index_map
        )
        for task in layer:
            task_to_depth_graph_map[task] = depth_graph

        tasks_with_supertasks = (
            task for task in layer if not graph.hierarchy_graph().is_top_level(task)
        )
        tasks_with_supertasks_sorted_by_descending_supertask_priority = sorted(
            tasks_with_supertasks,
            key=lambda task: task_to_supertask_priority_map[task],
            reverse=True,
        )

        tasks_with_subtasks = (
            task for task in layer if not graph.hierarchy_graph().is_concrete(task)
        )
        tasks_with_subtasks_sorted_by_descending_subtask_priority = sorted(
            tasks_with_subtasks,
            key=lambda task: task_to_subtask_priority_map[task],
            reverse=True,
        )

        hierarchy_layers.append(
            HierarchyLayer(
                tasks_with_supertasks_sorted_by_descending_supertask_priority,
                tasks_with_subtasks_sorted_by_descending_subtask_priority,
            )
        )

    # Populate initial depth positions
    task_to_depth_position_map = {
        task: starting_separation_distance * depth_index
        for task, depth_index in task_to_depth_index_map.items()
    }

    task_to_dependee_task_priority_map = {
        task: _get_dependee_tasks_priority(task, graph.dependency_graph())
        for task in graph.tasks()
    }

    task_to_dependent_task_priority_map = {
        task: _get_dependent_tasks_priority(task, graph.dependency_graph())
        for task in graph.tasks()
    }

    dependency_layers = list[DependencyLayer]()
    for layer in get_dependency_axis_groups(
        graph.tasks(), task_to_relation_layers_map=task_to_relation_layers_map
    ):
        tasks_with_dependee_tasks = (
            task for task in layer if not graph.dependency_graph().is_first(task)
        )
        tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority = sorted(
            tasks_with_dependee_tasks,
            key=lambda task: task_to_dependee_task_priority_map[task],
            reverse=True,
        )

        tasks_with_dependent_tasks = (
            task for task in layer if not graph.dependency_graph().is_last(task)
        )
        tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority = (
            sorted(
                tasks_with_dependent_tasks,
                key=lambda task: task_to_dependent_task_priority_map[task],
                reverse=True,
            )
        )

        dependency_layers.append(
            DependencyLayer(
                tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority,
                tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority,
            )
        )

    for _ in range(NUMBER_OF_DEPTH_POSITION_ITERATIONS):
        for layer in itertools.islice(hierarchy_layers, 1, None):
            for (
                task
            ) in layer.tasks_with_supertasks_sorted_by_descending_supertask_priority:
                ideal_position = _get_average_depth_position_of_supertasks(
                    task=task,
                    graph=graph.hierarchy_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                depth_graph = task_to_depth_graph_map[task]
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_supertask_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for layer in itertools.islice(reversed(hierarchy_layers), 1, None):
            for task in layer.tasks_with_subtasks_sorted_by_descending_subtask_priority:
                ideal_position = _get_average_depth_position_of_subtasks(
                    task=task,
                    graph=graph.hierarchy_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                depth_graph = task_to_depth_graph_map[task]
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_subtask_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for layer in itertools.islice(dependency_layers, 1, None):
            for task in layer.tasks_with_dependee_tasks_sorted_by_descending_dependee_task_priority:
                ideal_position = _get_average_depth_position_of_dependee_tasks(
                    task=task,
                    graph=graph.dependency_graph(),
                    task_to_depth_position_map=task_to_depth_position_map,
                )
                depth_graph = task_to_depth_graph_map[task]
                _move_task(
                    task=task,
                    ideal_position=ideal_position,
                    layer_depth_graph=depth_graph,
                    task_to_depth_position_map=task_to_depth_position_map,
                    task_to_priority_map=task_to_dependee_task_priority_map,
                    min_separation_distance=min_separation_distance,
                )

        for layer in itertools.islice(reversed(dependency_layers), 1, None):
            for task in layer.tasks_with_dependent_tasks_sorted_by_descending_dependent_task_priority:
                ideal_position = _get_average_depth_position_of_dependent_tasks(
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
