from collections.abc import Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_indexes import (
    get_depth_indexes_neighbour_median_and_transpose_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_positions import (
    get_depth_positions_naive_spacing_method,
    get_depth_positions_priority_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.dummy_tasks import (
    DummyUID,
    generate_graph_with_dummy_tasks,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.task_layers import (
    TaskRelationLayers,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


def get_depth_positions_unnamed_method(
    graph: tasks.INetworkGraphView,
    task_to_relation_layers_map: Mapping[tasks.UID, TaskRelationLayers],
    task_cylinder_radius: Radius,
) -> dict[tasks.UID, float]:
    (
        graph_with_dummies,
        task_or_dummy_to_relation_layers_map,
    ) = generate_graph_with_dummy_tasks(graph, task_to_relation_layers_map)

    task_or_dummy_to_depth_index_map = (
        get_depth_indexes_neighbour_median_and_transpose_method(
            graph_with_dummies, task_or_dummy_to_relation_layers_map
        )
    )

    # task_to_depth_position_map = get_depth_positions_naive_spacing_method(task_to_depth_index_map, separation_distance=12 * float(task_cylinder_radius))

    task_to_depth_position_map = get_depth_positions_priority_method(
        graph=graph_with_dummies,
        task_to_relation_layers_map=task_or_dummy_to_relation_layers_map,
        task_to_depth_index_map=task_or_dummy_to_depth_index_map,
        # TODO: These separation values were pulled out of thin air - more investigation required
        starting_separation_distance=10 * float(task_cylinder_radius),
        min_separation_distance=5 * float(task_cylinder_radius),
    )

    # Clear the dummy tasks
    dummy_tasks = [
        task for task in task_to_depth_position_map if isinstance(task, DummyUID)
    ]
    for dummy_task in dummy_tasks:
        del task_to_depth_position_map[dummy_task]

    return task_to_depth_position_map
