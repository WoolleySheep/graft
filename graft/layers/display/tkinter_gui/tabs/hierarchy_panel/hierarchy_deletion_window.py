import logging
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk
from typing import Final

from graft import architecture
from graft.domain import tasks
from graft.layers.display.tkinter_gui import event_broker

logger: Final = logging.getLogger(__name__)


def _get_hierarchies_with_names(
    logic_layer: architecture.LogicLayer,
) -> Generator[
    tuple[tuple[tasks.UID, tasks.Name], tuple[tasks.UID, tasks.Name]],
    None,
    None,
]:
    attributes_register = logic_layer.get_task_system().attributes_register()
    for supertask, subtask in (
        logic_layer.get_task_system().network_graph().hierarchy_graph().hierarchies()
    ):
        yield (
            (supertask, attributes_register[supertask].name),
            (subtask, attributes_register[subtask].name),
        )


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _format_hierarchy(
    supertask: tasks.UID,
    supertask_name: tasks.Name,
    subtask: tasks.UID,
    subtask_name: tasks.Name,
) -> str:
    formatted_supertask = _format_task_uid_name(supertask, supertask_name)
    formatted_subtask = _format_task_uid_name(subtask, subtask_name)
    return f"{formatted_supertask} -> {formatted_subtask}"


def _get_menu_options(
    logic_layer: architecture.LogicLayer,
) -> Generator[str, None, None]:
    hierarchies_with_names = sorted(
        _get_hierarchies_with_names(logic_layer=logic_layer),
        key=lambda x: (x[0][0], x[1][0]),
    )

    for (supertask, supertask_name), (subtask, subtask_name) in hierarchies_with_names:
        yield _format_hierarchy(supertask, supertask_name, subtask, subtask_name)


def _parse_task_uid_from_formatted_task_uid_name(
    formatted_task_uid_name: str,
) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _parse_task_uids_from_menu_option(menu_option: str) -> tuple[tasks.UID, tasks.UID]:
    formatted_tasks = menu_option.split(" -> ")
    if len(formatted_tasks) != 2:
        raise ValueError

    formatted_supertask, formatted_subtask = formatted_tasks
    supertask = _parse_task_uid_from_formatted_task_uid_name(formatted_supertask)
    subtask = _parse_task_uid_from_formatted_task_uid_name(formatted_subtask)
    return supertask, subtask


class HierarchyDeletionWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        self._logic_layer = logic_layer
        super().__init__(master=master)

        self.title("Delete hierarchy")

        menu_options = list(_get_menu_options(logic_layer=logic_layer))

        self._selected_hierarchy = tk.StringVar(self)
        self._hierarchy_option_menu = ttk.OptionMenu(
            self,
            self._selected_hierarchy,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._hierarchy_option_menu.grid(row=0, column=0)
        self._confirm_button.grid(row=1, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm hierarchy deletion button clicked")
        self._delete_hierarchy_between_selected_tasks_then_destroy_window()

    def _delete_hierarchy_between_selected_tasks_then_destroy_window(self) -> None:
        supertask, subtask = _parse_task_uids_from_menu_option(
            self._selected_hierarchy.get()
        )
        try:
            self._logic_layer.delete_task_hierarchy(supertask, subtask)
        except Exception:
            # TODO: Add error popup. For now, letting it propegate
            raise

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
