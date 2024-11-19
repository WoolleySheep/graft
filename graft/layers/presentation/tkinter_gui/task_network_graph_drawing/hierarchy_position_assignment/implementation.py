from collections.abc import Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


def get_hierarchy_layers_topologically_sorted_groups_method(
    graph: tasks.INetworkGraphView,
) -> dict[tasks.UID, int]:
    topologically_sorted_task_groups = (
        graph_conversion.convert_hierarchy_to_reduced_dag(
            graph.hierarchy_graph()
        ).topologically_sorted_groups()
    )

    hierarchy_positions = dict[tasks.UID, int]()
    for group_index, task_group in enumerate(topologically_sorted_task_groups):
        position = -group_index
        for task in task_group:
            hierarchy_positions[task] = position

    return hierarchy_positions


def get_hierarchy_positions_even_spacing_method(
    task_to_hierarchy_layer_map: Mapping[tasks.UID, int], task_cylinder_radius: Radius
) -> dict[tasks.UID, float]:
    return {
        task: 4 * float(task_cylinder_radius) * hierarchy_layer
        for task, hierarchy_layer in task_to_hierarchy_layer_map.items()
    }
