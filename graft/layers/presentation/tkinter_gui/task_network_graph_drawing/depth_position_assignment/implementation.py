from collections.abc import Mapping

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.position import (
    RelationPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


def get_depth_positions_cascade_method(
    graph: tasks.INetworkGraphView,
    relation_positions: Mapping[tasks.UID, RelationPosition],
    task_cylinder_radius: Radius,
) -> dict[tasks.UID, float]:
    return {
        task: 3 * float(task_cylinder_radius) * task_number
        for task_number, task in enumerate(relation_positions)
    }
