import collections
import dataclasses
import itertools
import statistics
from collections.abc import (
    Callable,
    Collection,
    Hashable,
    Iterable,
    Mapping,
    MutableMapping,
    Set,
)
from dataclasses import dataclass
from typing import Final

from graft import graphs
from graft.domain import tasks
from graft.domain.tasks.uid import TasksView
from graft.graphs.directed_acyclic_graph import DirectedAcyclicGraph
from graft.graphs.directed_graph_builder import DirectedGraphBuilder
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

NUMBER_OF_HIERARCHY_LAYER_DEPTH_INDEX_ITERATIONS: Final = 15


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
    return {
        task: index
        for index, group in enumerate(graph.topologically_sorted_groups())
        for task in group
    }


def _construct_depth_graph_of_hierarchy_layer(
    task_groups_along_dependency_axis: Iterable[Set[tasks.UID]],
    task_to_median_index_of_neighbours_map: Mapping[tasks.UID, float],
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    graph_builder = DirectedGraphBuilder[tasks.UID]()

    for task_group in task_groups_along_dependency_axis:
        for task in task_group:
            graph_builder.add_node(task)

        task_group_sorted_by_median_index = sorted(
            task_group,
            key=lambda task: (task_to_median_index_of_neighbours_map[task], task),
        )

        for task1, task2 in itertools.pairwise(task_group_sorted_by_median_index):
            graph_builder.add_edge(task1, task2)

    return DirectedAcyclicGraph(graph_builder.build().items())


def _construct_depth_graph_of_dependency_layer(
    task_groups_along_hierarchy_axis: Iterable[Iterable[tasks.UID]],
    task_to_median_index_of_neighbours_map: Mapping[tasks.UID, float],
) -> graphs.DirectedAcyclicGraph[tasks.UID]:
    graph_builder = DirectedGraphBuilder[tasks.UID]()
    for task_group in task_groups_along_hierarchy_axis:
        # Each task should only appear once, as tasks cannot be on multiple hierarchy levels
        for task in task_group:
            graph_builder.add_node(task)
        for task1, task2 in itertools.pairwise(
            sorted(
                task_group,
                key=lambda task: task_to_median_index_of_neighbours_map[task],
            )
        ):
            graph_builder.add_edge(task1, task2)

    return DirectedAcyclicGraph(graph_builder.build().items())


class DependencyLayer:
    def __init__(
        self,
        task_to_depth_index_map: MutableMapping[tasks.UID, int],
        hierarchy_layers: Collection[Collection[tasks.UID]],
    ) -> None:
        self.task_to_depth_index_map = task_to_depth_index_map
        self._hierarchy_layers = hierarchy_layers

    @property
    def hierarchy_layers(self) -> Collection[Collection[tasks.UID]]:
        return self._hierarchy_layers

    @property
    def tasks(self) -> tasks.TasksView:
        return tasks.TasksView(self.task_to_depth_index_map.keys())


def get_depth_indexes_neighbour_median_and_transpose_method(
    graph: tasks.NetworkGraph,
    relation_positions: Mapping[tasks.UID, TaskRelationLayers],
) -> dict[tasks.UID, int]:
    if not graph:
        return {}

    task_to_hierarchy_layer_map = dict[tasks.UID, HierarchyLayer]()

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
        hierarchy_layer = HierarchyLayer(
            task_to_depth_index_map,
            task_to_dependency_midpoint_map,
            dependency_groups,
        )
        hierarchy_layers.append(hierarchy_layer)
        for task in layer:
            task_to_hierarchy_layer_map[task] = hierarchy_layer

    task_to_dependency_layers = collections.defaultdict[
        tasks.UID, list[DependencyLayer]
    ](list)

    dependency_layers = list[DependencyLayer]()
    for dependency_group in get_dependency_axis_groups(
        graph.tasks(), relation_positions
    ):
        hierarchy_layers_in_dependency_layer = [
            hierarchy_layer.tasks & dependency_group
            for hierarchy_layer in hierarchy_layers
            if not hierarchy_layer.tasks.isdisjoint(dependency_group)
        ]
        dependency_layer = DependencyLayer(
            {task: i for i, task in enumerate(dependency_group)},
            hierarchy_layers_in_dependency_layer,
        )
        dependency_layers.append(dependency_layer)
        for task in dependency_group:
            task_to_dependency_layers.setdefault(task, []).append(dependency_layer)

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

            depth_graph = _construct_depth_graph_of_hierarchy_layer(
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

            depth_graph = _construct_depth_graph_of_hierarchy_layer(
                layer.dependency_groups, task_to_median_index_of_subtasks_map
            )

            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        for previous_layer, layer in itertools.pairwise(dependency_layers):

            def _get_ideal_index(
                task: tasks.UID,
                layer: DependencyLayer,
                previous_layer: DependencyLayer,
                graph: tasks.NetworkGraph,
            ) -> float:
                if (
                    task in previous_layer.tasks
                ):  # Task that stretches across multiple dependency levels
                    return previous_layer.task_to_depth_index_map[task]
                if not graph.dependency_graph().dependee_tasks(task):
                    return layer.task_to_depth_index_map[task]
                return _calculate_median_of_neighbours(
                    task,
                    graph.dependency_graph().dependee_tasks,
                    previous_layer.task_to_depth_index_map,
                )

            task_to_ideal_index_map = {
                task: _get_ideal_index(task, layer, previous_layer, graph)
                for task in layer.tasks
            }

            depth_graph = _construct_depth_graph_of_dependency_layer(
                task_groups_along_hierarchy_axis=layer.hierarchy_layers,
                task_to_median_index_of_neighbours_map=task_to_ideal_index_map,
            )
            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        for previous_layer, layer in itertools.pairwise(reversed(dependency_layers)):

            def _get_ideal_index(
                task: tasks.UID,
                layer: DependencyLayer,
                previous_layer: DependencyLayer,
                graph: tasks.NetworkGraph,
            ) -> float:
                if (
                    task in previous_layer.tasks
                ):  # Task that stretches across multiple dependency levels
                    return previous_layer.task_to_depth_index_map[task]
                if not graph.dependency_graph().dependent_tasks(task):
                    return layer.task_to_depth_index_map[task]
                return _calculate_median_of_neighbours(
                    task,
                    graph.dependency_graph().dependent_tasks,
                    previous_layer.task_to_depth_index_map,
                )

            task_to_ideal_index_map = {
                task: _get_ideal_index(task, layer, previous_layer, graph)
                for task in layer.tasks
            }

            depth_graph = _construct_depth_graph_of_dependency_layer(
                task_groups_along_hierarchy_axis=layer.hierarchy_layers,
                task_to_median_index_of_neighbours_map=task_to_ideal_index_map,
            )
            layer.task_to_depth_index_map = _get_topological_sort_group_indexes(
                depth_graph
            )

        # Merge hierarchy layers into dependency layers
        for dependency_layer in dependency_layers:
            graph_builder = DirectedGraphBuilder[tasks.UID]()
            for hierarchy_layer in dependency_layer.hierarchy_layers:

                def get_depth_index(task: tasks.UID) -> int:
                    return task_to_hierarchy_layer_map[task].task_to_depth_index_map[
                        task
                    ]

                tasks_in_layer_sorted_by_hierarchy_index = sorted(
                    hierarchy_layer,
                    key=get_depth_index,
                )
                for task in hierarchy_layer:
                    graph_builder.add_node(task)
                for shallower_task, deeper_task in itertools.pairwise(
                    tasks_in_layer_sorted_by_hierarchy_index
                ):
                    graph_builder.add_edge(shallower_task, deeper_task)
            depth_graph_from_hierarchy_info = graphs.DirectedAcyclicGraph[tasks.UID](
                graph_builder.build().items()
            )

            dependency_layer_task_to_index_from_hierarchies_map = (
                _get_topological_sort_group_indexes(depth_graph_from_hierarchy_info)
            )
            dependency_layer_task_to_combined_index_map = {
                task: dependency_depth_index
                + dependency_layer_task_to_index_from_hierarchies_map[task]
                for task, dependency_depth_index in dependency_layer.task_to_depth_index_map.items()
            }

            combined_depth_graph = _construct_depth_graph_of_dependency_layer(
                task_groups_along_hierarchy_axis=dependency_layer.hierarchy_layers,
                task_to_median_index_of_neighbours_map=dependency_layer_task_to_combined_index_map,
            )
            dependency_layer.task_to_depth_index_map = (
                _get_topological_sort_group_indexes(combined_depth_graph)
            )

        # Merge dependency layers into hierarchy layers
        for hierarchy_layer in hierarchy_layers:
            task_to_avg_dependency_index_map = {
                task: sum(
                    dependency_layer.task_to_depth_index_map[task]
                    for dependency_layer in task_to_dependency_layers[task]
                )
                / len(task_to_dependency_layers[task])
                for task in hierarchy_layer.tasks
            }

            dependency_depth_graph = _construct_depth_graph_of_hierarchy_layer(
                hierarchy_layer.dependency_groups, task_to_avg_dependency_index_map
            )

            task_to_combined_dependency_index_map = _get_topological_sort_group_indexes(
                dependency_depth_graph
            )

            hierarchy_layer_task_to_combined_index_map = {
                task: hierarchy_depth_index
                + task_to_combined_dependency_index_map[task]
                for task, hierarchy_depth_index in hierarchy_layer.task_to_depth_index_map.items()
            }

            combined_depth_graph = _construct_depth_graph_of_hierarchy_layer(
                task_groups_along_dependency_axis=hierarchy_layer.dependency_groups,
                task_to_median_index_of_neighbours_map=hierarchy_layer_task_to_combined_index_map,
            )
            hierarchy_layer.task_to_depth_index_map = (
                _get_topological_sort_group_indexes(combined_depth_graph)
            )

        # transpose(
        #     graph.hierarchy_graph(),
        #     hierarchy_layers,
        # )

    task_to_depth_index_map = dict[tasks.UID, int]()
    for layer in hierarchy_layers:
        task_to_depth_index_map.update(layer.task_to_depth_index_map)

    return task_to_depth_index_map
