from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import RED
from graft.layers.presentation.tkinter_gui.helpers.hierarchy_graph_failed_operation_window import (
    HierarchyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_delete_hierarchy_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task hierarchy deletion exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot delete a hierarchy as task [{e.task}] does not exist",
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.HierarchyDoesNotExistError as e:
        hierarchy_graph = tasks.HierarchyGraph(
            [(e.supertask, [e.subtask]), (e.subtask, [])]
        )
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot delete a hierarchy that does not exist",
            hierarchy_graph=hierarchy_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(
                colour=RED,
                connection_style=domain_visual_language.CURVED_ARROW_CONNECTION_STYLE,
            ),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
        )
        return False

    return True
