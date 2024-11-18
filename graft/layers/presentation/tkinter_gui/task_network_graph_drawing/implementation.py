from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.cylinder_position import (
    TaskCylinderPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment.implementation import (
    get_dependency_positions_unnamed_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment.implementation import (
    get_depth_positions_unnamed_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.hierarchy_position_assignment import (
    get_hierarchy_positions_topologically_sorted_groups_method,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.template import (
    calculate_task_positions,
)


def calculate_task_positions_unnamed_method(
    graph: tasks.INetworkGraphView, task_cylinder_radius: Radius
) -> dict[tasks.UID, TaskCylinderPosition]:
    return calculate_task_positions(
        graph=graph,
        task_cylinder_radius=task_cylinder_radius,
        get_dependency_positions=get_dependency_positions_unnamed_method,
        get_hierarchy_positions=get_hierarchy_positions_topologically_sorted_groups_method,
        get_depth_positions=get_depth_positions_unnamed_method,
    )
