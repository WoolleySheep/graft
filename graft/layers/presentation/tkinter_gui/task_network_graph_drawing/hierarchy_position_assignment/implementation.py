from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


def get_hierarchy_positions_topologically_sorted_groups_method(
    graph: tasks.INetworkGraphView,
    task_cylinder_radius: Radius,
) -> dict[tasks.UID, float]:
    reduced_dag = graph_conversion.convert_hierarchy_to_reduced_dag(
        graph.hierarchy_graph()
    )
    topologically_sorted_task_groups = reduced_dag.topologically_sorted_groups()

    hierarchy_positions = dict[tasks.UID, float]()
    for group_index, task_group in enumerate(topologically_sorted_task_groups):
        position = -3 * float(task_cylinder_radius) * group_index
        for task in task_group:
            hierarchy_positions[task] = position

    return hierarchy_positions
