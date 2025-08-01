from collections.abc import Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.component_separation import (
    get_depth_positions_with_component_adjustment,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_indexes import (
    get_depth_indexes_neighbour_median_and_transpose_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation.depth_positions import (
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
    task_to_depth_position_map = dict[tasks.UID, float]()

    # Evaluating each component separately, as their just going to be separated
    # depth-wise later. Avoids the issue where components would originally be located in
    # the same space (leading to some long task relationship lines), and then they'd be
    # separated, leaving things looking odd
    for component in graph.component_subgraphs():
        component_task_to_relation_layers_map = {
            task: relation_layers
            for task, relation_layers in task_to_relation_layers_map.items()
            if task in component.tasks()
        }
        (
            graph_with_dummies,
            task_or_dummy_to_relation_layers_map,
        ) = generate_graph_with_dummy_tasks(
            component, component_task_to_relation_layers_map
        )
        task_or_dummy_to_depth_index_map = (
            get_depth_indexes_neighbour_median_and_transpose_method(
                graph_with_dummies, task_or_dummy_to_relation_layers_map
            )
        )
        tmp_task_to_depth_position_map = get_depth_positions_priority_method(
            graph=graph_with_dummies,
            task_to_relation_layers_map=task_or_dummy_to_relation_layers_map,
            task_to_depth_index_map=task_or_dummy_to_depth_index_map,
            # TODO: These separation values were pulled out of thin air - more investigation required
            starting_separation_distance=20 * float(task_cylinder_radius),
            min_separation_distance=4 * float(task_cylinder_radius),
        )
        tmp_task_to_depth_position_map_without_dummies = {
            task: position
            for task, position in tmp_task_to_depth_position_map.items()
            if not isinstance(task, DummyUID)
        }
        task_to_depth_position_map.update(
            tmp_task_to_depth_position_map_without_dummies
        )

    return get_depth_positions_with_component_adjustment(
        graph=graph,
        task_to_position_map=task_to_depth_position_map,
        # TODO: Another separation value pulled out of my ass
        component_separation_distance=6 * float(task_cylinder_radius),
    )
