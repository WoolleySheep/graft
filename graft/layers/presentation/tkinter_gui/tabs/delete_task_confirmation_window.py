import functools
import tkinter as tk
from collections.abc import Callable
from tkinter import ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers.delete_task_error_windows import (
    convert_delete_task_exceptions_to_error_windows,
)


def _format_task_for_display(task: tasks.UID, name: tasks.Name) -> str:
    return f"[{task}] {name}" if name else f"[{task}]"


class TaskDeletionConfirmationWindow(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        task: tasks.UID,
        delete_task: Callable[[tasks.UID], None],
        get_task_name: Callable[[tasks.UID], tasks.Name],
    ) -> None:
        super().__init__(master)
        self._task = task
        self._delete_task = delete_task
        self._get_task_name = get_task_name

        self.title("Confirm Task Deletion")

        warning_message_label = ttk.Label(
            master=self, text="Are you sure you wish to delete the following task?"
        )
        task_name_label = ttk.Label(
            master=self, text=_format_task_for_display(task, self._get_task_name(task))
        )

        confirm_button = ttk.Button(master=self, text="Delete", command=self._delete)

        warning_message_label.grid(row=0, column=0)
        task_name_label.grid(row=1, column=0)
        confirm_button.grid(row=2, column=0)

    def _delete(self) -> None:
        if not convert_delete_task_exceptions_to_error_windows(
            functools.partial(self._delete_task, self._task),
            get_task_name=self._get_task_name,
            master=self,
        ):
            return

        broker = event_broker.get_singleton()
        broker.publish(event=event_broker.SystemModified())
        self.destroy()
