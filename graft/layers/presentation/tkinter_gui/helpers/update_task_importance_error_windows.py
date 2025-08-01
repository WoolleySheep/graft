from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    GREEN,
    WHITE,
)
from graft.layers.presentation.tkinter_gui.helpers.hierarchy_graph_failed_operation_window import (
    HierarchyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_update_task_importance_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task importance update exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot update importance as task [{e.task}] does not exist",
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.SuperiorTasksHaveImportanceError as e:
        subsystem = e.subsystem
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot update importance as task [{get_task_name(e.task)}] has superior tasks with importances",
            hierarchy_graph=subsystem.network_graph().hierarchy_graph(),
            get_task_properties=lambda task: domain_visual_language.get_graph_node_properties(
                colour=domain_visual_language.get_task_colour_by_importance(
                    importance=subsystem.attributes_register()[task].importance
                ),
                alpha_level=domain_visual_language.GraphAlphaLevel.DEFAULT
                if subsystem.attributes_register()[task].importance is not None
                else domain_visual_language.GraphAlphaLevel.FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(
                alpha_level=domain_visual_language.GraphAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_importance(
                            e.importance
                        ),
                        edge_colour=GREEN,
                        alpha_level=domain_visual_language.GraphAlphaLevel.DEFAULT,
                    ),
                    {e.task},
                ),
            ],
            legend_elements=[
                (
                    "high importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.HIGH_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "medium importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.MEDIUM_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "low importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.LOW_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "task",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=GREEN
                    ),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_graph_edge_properties(),
                ),
            ],
        )
        return False
    except tasks.InferiorTasksHaveImportanceError as e:
        subsystem = e.subsystem
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot update importance as task [{get_task_name(e.task)}] has inferior tasks with importances",
            hierarchy_graph=subsystem.network_graph().hierarchy_graph(),
            get_task_properties=lambda task: domain_visual_language.get_graph_node_properties(
                colour=domain_visual_language.get_task_colour_by_importance(
                    importance=subsystem.attributes_register()[task].importance
                ),
                alpha_level=domain_visual_language.GraphAlphaLevel.DEFAULT
                if subsystem.attributes_register()[task].importance is not None
                else domain_visual_language.GraphAlphaLevel.FADED,
            ),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(
                alpha_level=domain_visual_language.GraphAlphaLevel.FADED
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    None,
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.get_task_colour_by_importance(
                            e.importance
                        ),
                        edge_colour=GREEN,
                        alpha_level=domain_visual_language.GraphAlphaLevel.DEFAULT,
                    ),
                    {e.task},
                ),
            ],
            legend_elements=[
                (
                    "high importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.HIGH_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "medium importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.MEDIUM_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "low importance",
                    domain_visual_language.get_graph_node_properties(
                        colour=domain_visual_language.LOW_IMPORTANCE_COLOUR
                    ),
                ),
                (
                    "task",
                    domain_visual_language.get_graph_node_properties(
                        colour=WHITE, edge_colour=GREEN
                    ),
                ),
                (
                    "hierarchy",
                    domain_visual_language.get_graph_edge_properties(),
                ),
            ],
        )
        return False

    return True
