
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.cylinder_position import (
    XAxisCylinderPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.layers_assignment import (
    get_layers_unnamed_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.template import (
    calculate_task_positions,
)


def calculate_task_positions_modified_sugiyama_method(
    graph: tasks.INetworkGraphView, task_cylinder_radius: float
) -> dict[tasks.UID, XAxisCylinderPosition]:
    return calculate_task_positions(graph=graph, task_cylinder_radius=task_cylinder_radius, get_layers_fn=get_layers_unnamed_method)


def calculate_task_positions_hardcoded(
    graph: tasks.INetworkGraphView, task_cylinder_radius: float
) -> dict[tasks.UID, XAxisCylinderPosition]:
    task_positions = dict[tasks.UID, XAxisCylinderPosition]()
    for count, task in enumerate(graph.tasks()):
        task_positions[task] = XAxisCylinderPosition(
            x_min=2 * count, x_max=2 * count + 1, y=count, z=count
        )
    return task_positions
