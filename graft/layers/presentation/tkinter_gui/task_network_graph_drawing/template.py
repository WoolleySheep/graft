from graft.domain import tasks
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.cylinder_position import (
    TaskCylinderPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.dependency_position_assignment import (
    GetDependencyPositions,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.depth_position_assignment import (
    GetDepthPositions,
    RelationPosition,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.hierarchy_position_assignment import (
    GetHierarchyPositions,
)
from graft.layers.presentation.tkinter_gui.task_network_graph_drawing.radius import (
    Radius,
)


def calculate_task_positions(
    graph: tasks.INetworkGraphView,
    task_cylinder_radius: Radius,
    get_hierarchy_positions: GetHierarchyPositions,
    get_dependency_positions: GetDependencyPositions,
    get_depth_positions: GetDepthPositions,
) -> dict[tasks.UID, TaskCylinderPosition]:
    dependency_positions = get_dependency_positions(graph=graph)

    hierarchy_positions = get_hierarchy_positions(
        graph=graph, task_cylinder_radius=task_cylinder_radius
    )

    relation_positions = {
        task: RelationPosition(
            dependency_position=dependency_positions[task],
            hierarchy_position=hierarchy_positions[task],
        )
        for task in graph.tasks()
    }

    depth_positions = get_depth_positions(
        graph=graph,
        relation_positions=relation_positions,
        task_cylinder_radius=task_cylinder_radius,
    )

    return {
        task: TaskCylinderPosition(
            min_dependency_position=dependency_positions[task].min - 0.25,
            max_dependency_position=dependency_positions[task].max + 0.25,
            hierarchy_position=hierarchy_positions[task],
            depth_position=depth_positions[task],
        )
        for task in graph.tasks()
    }
