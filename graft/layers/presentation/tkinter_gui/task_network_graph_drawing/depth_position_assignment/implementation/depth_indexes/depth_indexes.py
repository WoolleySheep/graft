import itertools
import statistics
from collections.abc import (
    Callable,
    Hashable,
    Iterable,
    Mapping,
    Set,
)
from typing import Final

from graft import graphs
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.dependency_axis_grouping import (
    get_dependency_axis_groups,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_indexes.hierarchy_layer import (
    HierarchyLayer,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_indexes.transpose import (
    transpose,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
    get_hierarchy_layers_in_descending_order,
)

NUMBER_OF_HIERARCHY_LAYER_DEPTH_INDEX_ITERATIONS: Final = 20


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
    graph: tasks.IHierarchyGraphView,
    task_to_index_map: Mapping[tasks.UID, int],
) -> float:
    return _calculate_median_of_neighbours(
        node=task, get_neighbours=graph.supertasks, node_to_value_map=task_to_index_map
    )


def _calculate_median_index_of_subtasks(
    task: tasks.UID,
    graph: tasks.IHierarchyGraphView,
    task_to_index_map: Mapping[tasks.UID, int],
) -> float:
    return _calculate_median_of_neighbours(
        node=task, get_neighbours=graph.subtasks, node_to_value_map=task_to_index_map
    )


def _get_topological_sort_group_indexes[T: Hashable](
    graph: graphs.DirectedAcyclicGraph[T],
) -> dict[T, int]:
    task_to_topological_sort_group_index_map = dict[T, int]()
    for index, group in enumerate(graph.topologically_sorted_groups()):
        for task in group:
            task_to_topological_sort_group_index_map[task] = index

    return task_to_topological_sort_group_index_map


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
            if (
                (task1, task2) in depth_graph.edges()
                or task1 == task2
                or task1 in depth_graph.descendants([task2])
            ):
                continue

            depth_graph.add_edge(task1, task2)

    return depth_graph


def get_depth_indexes_neighbour_median_and_transpose_method(
    graph: tasks.NetworkGraph,
    relation_positions: Mapping[tasks.UID, TaskRelationLayers],
) -> dict[tasks.UID, int]:
    hierarchy_layers = list[HierarchyLayer]()
    for layer in get_hierarchy_layers_in_descending_order(relation_positions):
        task_to_depth_index_map = {task: index for index, task in enumerate(layer)}
        task_to_dependency_midpoint_map = {
            task: (
                relation_positions[task].dependency.max
                - relation_positions[task].dependency.min
            )
            / 2
            + relation_positions[task].dependency.min
            for task in layer
        }
        dependency_groups = list(get_dependency_axis_groups(layer, relation_positions))
        hierarchy_layers.append(
            HierarchyLayer(
                task_to_depth_index_map,
                task_to_dependency_midpoint_map,
                dependency_groups,
            )
        )

    for _ in range(NUMBER_OF_HIERARCHY_LAYER_DEPTH_INDEX_ITERATIONS):
        # Go top-to-bottom, then bottom-to-top. Flip the dependency graph
        # resolution order from back-to-front then front-to-back.

        for previous_layer, layer in itertools.pairwise(hierarchy_layers):
            task_to_median_index_of_supertasks_map = {
                task: _calculate_median_index_of_supertasks(
                    task,
                    graph.hierarchy_graph(),
                    previous_layer.task_to_depth_index_map,
                )
                if graph.hierarchy_graph().supertasks(task)
                else depth_index
                for task, depth_index in layer.task_to_depth_index_map.items()
            }

            depth_graph = _construct_depth_graph(
                layer.dependency_groups, task_to_median_index_of_supertasks_map
            )

            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        for previous_layer, layer in itertools.pairwise(reversed(hierarchy_layers)):
            task_to_median_index_of_subtasks_map = {
                task: _calculate_median_index_of_subtasks(
                    task,
                    graph.hierarchy_graph(),
                    previous_layer.task_to_depth_index_map,
                )
                if graph.hierarchy_graph().subtasks(task)
                else depth_index
                for task, depth_index in layer.task_to_depth_index_map.items()
            }

            depth_graph = _construct_depth_graph(
                layer.dependency_groups, task_to_median_index_of_subtasks_map
            )

            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        for previous_layer, layer in itertools.pairwise(hierarchy_layers):
            task_to_median_index_of_supertasks_map = {
                task: _calculate_median_index_of_supertasks(
                    task,
                    graph.hierarchy_graph(),
                    previous_layer.task_to_depth_index_map,
                )
                if graph.hierarchy_graph().supertasks(task)
                else depth_index
                for task, depth_index in layer.task_to_depth_index_map.items()
            }

            depth_graph = _construct_depth_graph(
                reversed(layer.dependency_groups),
                task_to_median_index_of_supertasks_map,
            )

            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        for previous_layer, layer in itertools.pairwise(reversed(hierarchy_layers)):
            task_to_median_index_of_subtasks_map = {
                task: _calculate_median_index_of_subtasks(
                    task,
                    graph.hierarchy_graph(),
                    previous_layer.task_to_depth_index_map,
                )
                if graph.hierarchy_graph().subtasks(task)
                else depth_index
                for task, depth_index in layer.task_to_depth_index_map.items()
            }

            depth_graph = _construct_depth_graph(
                reversed(layer.dependency_groups), task_to_median_index_of_subtasks_map
            )

            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        transpose(
            graph.hierarchy_graph(),
            hierarchy_layers,
        )

    task_to_depth_index_map = dict[tasks.UID, int]()
    for layer in hierarchy_layers:
        task_to_depth_index_map.update(layer.task_to_depth_index_map)

    return task_to_depth_index_map
