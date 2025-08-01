import itertools
from collections.abc import Callable
from tkinter import Misc

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import domain_visual_language
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    GREEN,
    PURPLE,
    RED,
    YELLOW,
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


def convert_delete_task_exceptions_to_error_windows(
    func: Callable[[], None],
    get_task_name: Callable[[tasks.UID], tasks.Name],
    master: Misc,
) -> bool:
    """Catch task deletion exceptions and display the matching error window.

    If the function succeeds, returns True. If the function raises an exception and an
    error window is shown, return False.
    """
    try:
        func()
    except tasks.TaskDoesNotExistError as e:
        HierarchyGraphOperationFailedWindow(
            master=master,
            description_text=f"Cannot delete as [{e.task}] does not exist",
            hierarchy_graph=tasks.HierarchyGraph(),
            get_task_properties=lambda _: domain_visual_language.get_graph_node_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_graph_edge_properties(),
        )
        return False
    except tasks.HasNeighboursError as e:
        hierarchy_graph = tasks.HierarchyGraph(
            itertools.chain(
                ((supertask, [e.task]) for supertask in e.supertasks),
                [(e.task, e.subtasks)],
                ((subtask, []) for subtask in e.subtasks),
                ((dependee_task, []) for dependee_task in e.dependee_tasks),
                ((dependent_task, []) for dependent_task in e.dependent_tasks),
            )
        )

        dependency_graph = tasks.DependencyGraph(
            itertools.chain(
                ((dependee_task, [e.task]) for dependee_task in e.dependee_tasks),
                [(e.task, e.dependent_tasks)],
                ((dependent_task, []) for dependent_task in e.dependent_tasks),
                ((supertask, []) for supertask in e.supertasks),
                ((subtask, []) for subtask in e.subtasks),
            )
        )
        network_graph = tasks.NetworkGraph(
            dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
        )
        NetworkGraphOperationFailedWindow(
            master=master,
            description_text="Cannot delete task that has neighbours",
            task_network=network_graph,
            get_task_properties=lambda _: domain_visual_language.get_network_task_properties(),
            get_hierarchy_properties=lambda _,
            __: domain_visual_language.get_network_hierarchy_properties(),
            get_dependency_properties=lambda _,
            __: domain_visual_language.get_network_dependency_properties(),
            get_task_annotation_text=lambda task: format_task_name_for_annotation(
                get_task_name(task)
            ),
            highlighted_task_groups=[
                (
                    "supertasks",
                    domain_visual_language.get_network_task_properties(colour=RED),
                    e.supertasks,
                ),
                (
                    "subtasks",
                    domain_visual_language.get_network_task_properties(colour=GREEN),
                    e.subtasks,
                ),
                (
                    "dependee tasks",
                    domain_visual_language.get_network_task_properties(colour=PURPLE),
                    e.dependee_tasks,
                ),
                (
                    "dependent tasks",
                    domain_visual_language.get_network_task_properties(colour=YELLOW),
                    e.dependent_tasks,
                ),
            ],
            legend_elements=[
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
