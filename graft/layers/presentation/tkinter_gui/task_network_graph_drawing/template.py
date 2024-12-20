from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.cylinder_position import (
    TaskCylinderPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment import (
    GetDependencyPositions,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment import (
    GetDepthPositions,
    TaskRelationLayers,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.hierarchy_position_assignment import (
    GetHierarchyLayers,
    GetHierarchyPositions,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)

#  When the task cylinder length is 0, it would  appear as a flat disk. To make
#  sure it always appears as a nice cylinder, add a small offset to each end.
#  The minimum dependency distance between cylinders is 1, so the offset should
#  be small enough that even if task cylinders are colinear, they do not touch.
_TASK_CYLINDER_LENGTH_OFFSET: Final = 0.25


def calculate_task_positions(
    graph: tasks.INetworkGraphView,
    task_cylinder_radius: Radius,
    get_hierarchy_layers: GetHierarchyLayers,
    get_hierarchy_positions: GetHierarchyPositions,
    get_dependency_positions: GetDependencyPositions,
    get_depth_positions: GetDepthPositions,
) -> dict[tasks.UID, TaskCylinderPosition]:
    dependency_positions = get_dependency_positions(graph=graph)

    hierarchy_layers = get_hierarchy_layers(graph=graph)

    hierarchy_positions = get_hierarchy_positions(
        task_to_hierarchy_layer_map=hierarchy_layers,
        task_cylinder_radius=task_cylinder_radius,
    )

    task_to_relation_layers_map = {
        task: TaskRelationLayers(
            dependency_layers=dependency_positions[task],
            hierarchy_layer=hierarchy_layers[task],
        )
        for task in graph.tasks()
    }

    depth_positions = get_depth_positions(
        graph=graph,
        task_to_relation_layers_map=task_to_relation_layers_map,
        task_cylinder_radius=task_cylinder_radius,
    )

    return {
        task: TaskCylinderPosition(
            min_dependency_position=dependency_positions[task].min
            - _TASK_CYLINDER_LENGTH_OFFSET,
            max_dependency_position=dependency_positions[task].max
            + _TASK_CYLINDER_LENGTH_OFFSET,
            hierarchy_position=hierarchy_positions[task],
            depth_position=depth_positions[task],
        )
        for task in graph.tasks()
    }
