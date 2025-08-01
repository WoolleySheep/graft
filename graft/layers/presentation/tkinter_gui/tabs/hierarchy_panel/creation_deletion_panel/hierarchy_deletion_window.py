import logging
import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import ttk
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers.delete_hierarchy_error_windows import (
    convert_delete_hierarchy_exceptions_to_error_windows,
)

logger: Final = logging.getLogger(__name__)


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _format_hierarchy_menu_option(
    supertask: tasks.UID,
    subtask: tasks.UID,
    get_task_name: Callable[[tasks.UID], tasks.Name],
) -> str:
    supertask_name = get_task_name(supertask)
    subtask_name = get_task_name(subtask)
    formatted_supertask = _format_task_uid_name(supertask, supertask_name)
    formatted_subtask = _format_task_uid_name(subtask, subtask_name)
    return f"{formatted_supertask} -> {formatted_subtask}"


def _parse_task_uid_from_formatted_task_uid_name(
    formatted_task_uid_name: str,
) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _parse_hierarchy_from_menu_option(menu_option: str) -> tuple[tasks.UID, tasks.UID]:
    formatted_tasks = menu_option.split(" -> ")
    if len(formatted_tasks) != 2:
        raise ValueError

    formatted_supertask, formatted_subtask = formatted_tasks
    supertask = _parse_task_uid_from_formatted_task_uid_name(formatted_supertask)
    subtask = _parse_task_uid_from_formatted_task_uid_name(formatted_subtask)
    return supertask, subtask


class HierarchyDeletionWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        hierarchy_options: Sequence[tuple[tasks.UID, tasks.UID]],
        delete_hierarchy: Callable[[tasks.UID, tasks.UID], None],
        get_task_name: Callable[[tasks.UID], tasks.Name],
    ) -> None:
        super().__init__(master=master)
        self._delete_hierarchy = delete_hierarchy
        self._get_task_name = get_task_name

        self.title("Delete hierarchy")

        menu_options = [
            _format_hierarchy_menu_option(
                supertask,
                subtask,
                get_task_name,
            )
            for supertask, subtask in hierarchy_options
        ]

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
        supertask, subtask = _parse_hierarchy_from_menu_option(
            self._selected_hierarchy.get()
        )

        if not convert_delete_hierarchy_exceptions_to_error_windows(
            func=lambda: self._delete_hierarchy(supertask, subtask),
            get_task_name=self._get_task_name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
