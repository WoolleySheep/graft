from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.helpers import graph_conversion


def get_hierarchy_positions_topologically_sorted_groups_method(
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
