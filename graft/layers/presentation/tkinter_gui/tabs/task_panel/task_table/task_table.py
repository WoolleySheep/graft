import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers.task_table.task_table_with_name import (
    TaskTableWithName,
)


class TaskTable(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._show_completed_tasks = tk.BooleanVar()
        self._show_completed_tasks_checkbutton = ttk.Checkbutton(
            self,
            text="Show completed tasks",
            variable=self._show_completed_tasks,
            command=self._on_show_completed_tasks_button_toggled,
        )
        self._show_completed_tasks.set(False)

        self._task_table = TaskTableWithName(master=self)

        self._show_completed_tasks_checkbutton.grid(row=0, column=0)
        self._task_table.grid(row=1, column=0)

        self._update_tasks()

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: self._update_tasks())

    def _get_task_name(self, task: tasks.UID) -> tasks.Name:
        return self._logic_layer.get_task_system().attributes_register()[task].name

    def _update_tasks(self) -> None:
        self._task_table.update_tasks(
            (task, self._get_task_name(task))
            for task in self._get_tasks_matching_current_filter()
        )

    def _get_tasks_matching_current_filter(self) -> tasks.TasksView:
        return (
            self._logic_layer.get_task_system().tasks()
            if self._show_completed_tasks.get()
            else tasks.get_incomplete_system(
                self._logic_layer.get_task_system()
            ).tasks()
        )

    def _on_show_completed_tasks_button_toggled(self) -> None:
        self._update_tasks()
