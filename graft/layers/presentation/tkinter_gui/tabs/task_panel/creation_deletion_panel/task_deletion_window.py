import itertools
import logging
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.domain.tasks.network_graph import NetworkGraph
from graft.layers.presentation.tkinter_gui import (
    domain_visual_language,
    event_broker,
    helpers,
)
from graft.layers.presentation.tkinter_gui.helpers import (
    format_task_name_for_annotation,
)
from graft.layers.presentation.tkinter_gui.helpers.colour import (
    GREEN,
    PURPLE,
    RED,
    YELLOW,
)

logger = logging.getLogger(__name__)


def _get_task_uids_with_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[tuple[tasks.UID, tasks.Name], None, None]:
    """Yield pairs of task UIDs and task names."""
    for uid, attributes in logic_layer.get_task_system().attributes_register().items():
        yield uid, attributes.name


def _format_task_uid_with_name_as_menu_option(
    task_uid: tasks.UID, task_name: tasks.Name
) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    task_uids_names = sorted(
        _get_task_uids_with_names(logic_layer=logic_layer), key=lambda x: x[0]
    )
    for uid, name in task_uids_names:
        yield _format_task_uid_with_name_as_menu_option(uid, name)


def _parse_task_uid_from_menu_option(menu_option: str) -> tasks.UID:
    first_closing_square_bracket = menu_option.find("]")
    uid_number = int(menu_option[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


class TaskDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self._logic_layer = logic_layer
        super().__init__(master=master)

        self.title("Delete task")

        self._selected_task = tk.StringVar(self)
        menu_options = list(_get_menu_options(logic_layer=logic_layer))
        self._task_selection = ttk.OptionMenu(
            self,
            self._selected_task,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._confirm_button = ttk.Button(
            self, text="Confirm", command=self._on_confirm_button_clicked
        )

        self._task_selection.grid(row=0, column=0)
        self._confirm_button.grid(row=1, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm task deletion button clicked")
        self._delete_selected_task_then_destroy_window()

    def _delete_selected_task_then_destroy_window(self) -> None:
        task = _parse_task_uid_from_menu_option(self._selected_task.get())
        try:
            self._logic_layer.delete_task(task)
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
            network_graph = NetworkGraph(
                dependency_graph=dependency_graph, hierarchy_graph=hierarchy_graph
            )
            helpers.NetworkGraphOperationFailedWindow(
                master=self,
                description_text="Cannot delete task that has neighbours",
                task_network=network_graph,
                get_task_properties=lambda _: domain_visual_language.get_network_task_properties(),
                get_hierarchy_properties=lambda _,
                __: domain_visual_language.get_network_hierarchy_properties(),
                get_dependency_properties=lambda _,
                __: domain_visual_language.get_network_dependency_properties(),
                get_task_annotation_text=lambda task: format_task_name_for_annotation(
                    self._logic_layer.get_task_system().attributes_register()[task].name
                ),
                highlighted_task_groups=[
                    (
                        "supertasks",
                        domain_visual_language.get_network_task_properties(colour=RED),
                        e.supertasks,
                    ),
                    (
                        "subtasks",
                        domain_visual_language.get_network_task_properties(
                            colour=GREEN
                        ),
                        e.subtasks,
                    ),
                    (
                        "dependee tasks",
                        domain_visual_language.get_network_task_properties(
                            colour=PURPLE
                        ),
                        e.dependee_tasks,
                    ),
                    (
                        "dependent tasks",
                        domain_visual_language.get_network_task_properties(
                            colour=YELLOW
                        ),
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
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
