from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.cylinder_position import (
    XAxisCylinderPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.layers_assignment import (
    GetLayersFn,
)


def calculate_task_positions(
    graph: tasks.INetworkGraphView,
    task_cylinder_radius: float,
    get_layers_fn: GetLayersFn,
) -> dict[tasks.UID, XAxisCylinderPosition]:
    get_layers_fn(graph)
