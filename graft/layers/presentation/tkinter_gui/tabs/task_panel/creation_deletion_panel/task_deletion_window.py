import functools
import logging
import tkinter as tk
from collections.abc import Generator
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import (
    event_broker,
)
from graft.layers.presentation.tkinter_gui.helpers.delete_task_error_windows import (
    convert_delete_task_exceptions_to_error_windows,
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

        if not convert_delete_task_exceptions_to_error_windows(
            functools.partial(self._logic_layer.delete_task, task=task),
            get_task_name=lambda task: self._logic_layer.get_task_system()
            .attributes_register()[task]
            .name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event_broker.SystemModified())
        self.destroy()
