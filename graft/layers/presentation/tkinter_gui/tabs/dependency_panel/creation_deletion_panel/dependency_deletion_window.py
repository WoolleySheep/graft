import logging
import tkinter as tk
from collections.abc import Callable, Sequence
from tkinter import ttk
from typing import Final

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers.delete_dependency_error_windows import (
    convert_delete_dependency_exceptions_to_error_windows,
)

logger: Final = logging.getLogger(__name__)


def _format_task_uid_name(task_uid: tasks.UID, task_name: tasks.Name) -> str:
    return f"[{task_uid}] {task_name}" if task_name else f"[{task_uid}]"


def _format_dependency_menu_option(
    dependee_task: tasks.UID,
    dependent_task: tasks.UID,
    get_task_name: Callable[[tasks.UID], tasks.Name],
) -> str:
    dependee_task_name = get_task_name(dependee_task)
    dependent_task_name = get_task_name(dependent_task)
    formatted_dependee_task = _format_task_uid_name(dependee_task, dependee_task_name)
    formatted_dependent_task = _format_task_uid_name(
        dependent_task, dependent_task_name
    )
    return f"{formatted_dependee_task} -> {formatted_dependent_task}"


def _parse_task_uid_from_formatted_task_uid_name(
    formatted_task_uid_name: str,
) -> tasks.UID:
    first_closing_square_bracket = formatted_task_uid_name.find("]")
    uid_number = int(formatted_task_uid_name[1:first_closing_square_bracket])
    return tasks.UID(uid_number)


def _parse_dependency_from_menu_option(menu_option: str) -> tuple[tasks.UID, tasks.UID]:
    formatted_tasks = menu_option.split(" -> ")
    if len(formatted_tasks) != 2:
        raise ValueError

    formatted_dependee_task, formatted_dependent_task = formatted_tasks
    dependee_task = _parse_task_uid_from_formatted_task_uid_name(
        formatted_dependee_task
    )
    dependent_task = _parse_task_uid_from_formatted_task_uid_name(
        formatted_dependent_task
    )
    return dependee_task, dependent_task


class DependencyDeletionWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        dependency_options: Sequence[tuple[tasks.UID, tasks.UID]],
        delete_dependency: Callable[[tasks.UID, tasks.UID], None],
        get_task_name: Callable[[tasks.UID], tasks.Name],
    ) -> None:
        super().__init__(master=master)
        self._delete_dependency = delete_dependency
        self._get_task_name = get_task_name

        self.title("Delete dependency")

        menu_options = [
            _format_dependency_menu_option(
                dependee_task,
                dependent_task,
                get_task_name,
            )
            for dependee_task, dependent_task in dependency_options
        ]

        self._selected_dependency = tk.StringVar(self)
        self._dependency_option_menu = ttk.OptionMenu(
            self,
            self._selected_dependency,
            menu_options[0] if menu_options else None,
            *menu_options,
        )

        self._confirm_button = ttk.Button(
            self,
            text="Confirm",
            command=self._on_confirm_button_clicked,
        )

        self._dependency_option_menu.grid(row=0, column=0)
        self._confirm_button.grid(row=1, column=0)

    def _on_confirm_button_clicked(self) -> None:
        logger.info("Confirm dependency deletion button clicked")
        self._delete_dependency_between_selected_tasks_then_destroy_window()

    def _delete_dependency_between_selected_tasks_then_destroy_window(self) -> None:
        dependee_task, dependent_task = _parse_dependency_from_menu_option(
            self._selected_dependency.get()
        )

        if not convert_delete_dependency_exceptions_to_error_windows(
            func=lambda: self._delete_dependency(dependee_task, dependent_task),
            get_task_name=self._get_task_name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
