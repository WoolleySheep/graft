from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import RED
from graft.layers.presentation.tkinter_gui.helpers.dependency_graph_failed_operation_window import (
    DependencyGraphOperationFailedWindow,
)
from graft.layers.presentation.tkinter_gui.helpers.static_graph import (
    format_task_name_for_annotation,
)


def convert_delete_dependency_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task dependency deletion exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot delete a dependency as task [{e.task}] does not exist",
            dependency_graph=tasks.DependencyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.DependencyDoesNotExistError as e:
        dependency_graph = tasks.DependencyGraph(
            [(e.dependee_task, [e.dependent_task]), (e.dependent_task, [])]
        )
        DependencyGraphOperationFailedWindow(
            master=master,
            description_text="Cannot delete a dependency that does not exist",
            dependency_graph=dependency_graph,
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_dependency_properties=lambda _,
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
