from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import RED, WHITE
from graft.layers.presentation.tkinter_gui.helpers.graph_node_drawing_properties import (
    GraphNodeDrawingProperties,
)
from graft.layers.presentation.tkinter_gui.helpers.hierarchy_graph_failed_operation_window import (
    HierarchyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.network_graph_failed_operation_window import (
    NetworkGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_update_task_progress_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task progress update exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot update progress as task [{e.task}] does not exist",
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.NotConcreteTaskError as e:
        hierarchy_graph = tasks.HierarchyGraph([(e.task, e.subtasks)])
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot update progress as task is not concrete",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                ("subtask", GraphNodeDrawingProperties(colour=RED), e.subtasks)
            ],
        )
        return False
    except tasks.DownstreamTasksHaveStartedError as e:
        subsystem = e.subsystem  # Bind to local scope
        started_downstream_tasks_to_progress_map = (
            e.started_downstream_tasks_to_progress_map
        )  # Bind to local scope
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot update progress to incomplete as downstream tasks have started",
            task_network=e.subsystem.network_graph(),
            get_task_properties=lambda task: domain_visual_language.get_network_task_properties(
                colour=domain_visual_language.get_task_colour_by_progress(
                    subsystem.get_progress(task)
                ),
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
                if task in started_downstream_tasks_to_progress_map
                else domain_visual_language.NetworkAlphaLevel.VERY_FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.progress
                        ),
                        edge_colour=RED,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.task},
                )
            ],
            legend_elements=[
                (
                    "completed",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR
                    ),
                ),
                (
                    "in progress",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.IN_PROGRESS_TASK_COLOUR
                    ),
                ),
                (
                    "not started",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR
                    ),
                ),
                (
                    "task",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=RED
                    ),
                ),
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False
    except tasks.UpstreamTasksAreIncompleteError as e:
        subsystem = e.subsystem  # Bind to local scope
        incomplete_upstream_tasks_to_progress_map = (
            e.incomplete_upstream_tasks_to_progress_map
        )  # Bind to local scope
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot update progress to started as upstream tasks are incomplete",
            task_network=e.subsystem.network_graph(),
            get_task_properties=lambda task: domain_visual_language.get_network_task_properties(
                colour=domain_visual_language.get_task_colour_by_progress(
                    subsystem.get_progress(task)
                ),
                alpha_level=domain_visual_language.NetworkAlphaLevel.DEFAULT
                if task in incomplete_upstream_tasks_to_progress_map
                else domain_visual_language.NetworkAlphaLevel.VERY_FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(
                alpha_level=domain_visual_language.NetworkAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.get_task_colour_by_progress(
                            e.progress
                        ),
                        edge_colour=RED,
                        alpha_level=domain_visual_language.NetworkAlphaLevel.HIGHLIGHTED,
                    ),
                    {e.task},
                )
            ],
            legend_elements=[
                (
                    "completed",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.COMPLETED_TASK_COLOUR
                    ),
                ),
                (
                    "in progress",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.IN_PROGRESS_TASK_COLOUR
                    ),
                ),
                (
                    "not started",
                    domain_visual_language.get_network_task_properties(
                        colour=domain_visual_language.NOT_STARTED_TASK_COLOUR
                    ),
                ),
                (
                    "task",
                    domain_visual_language.get_network_task_properties(
                        colour=WHITE, edge_colour=RED
                    ),
                ),
                (
                    "dependency",
                    domain_visual_language.get_network_dependency_properties(),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_network_hierarchy_properties(),
                ),
            ],
        )
        return False

    return True
