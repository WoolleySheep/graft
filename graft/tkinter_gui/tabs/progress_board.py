import tkinter as tk

from graft import architecture
from graft.tkinter_gui import event_broker
from graft.tkinter_gui.helpers import TaskTable


class ProgressBoard(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._concrete_header = tk.Label(self, text="Concrete")
        self._non_concrete_header = tk.Label(self, text="Not Concrete")

        self._not_started_header = tk.Label(self, text="Not Started")
        self._not_started_non_concrete_tasks = TaskTable(self)
        self._not_started_concrete_tasks = TaskTable(self)

        self._in_progress_header = tk.Label(self, text="In Progress")
        self._in_progress_non_concrete_tasks = TaskTable(self)
        self._in_progress_concrete_tasks = TaskTable(self)

        self._completed_header = tk.Label(self, text="Completed")
        self._completed_non_concrete_tasks = TaskTable(self)
        self._completed_concrete_tasks = TaskTable(self)

        self._non_concrete_header.grid(row=1, column=0)
        self._concrete_header.grid(row=2, column=0)

        self._not_started_header.grid(row=0, column=1)
        self._not_started_non_concrete_tasks.grid(row=1, column=1)
        self._not_started_concrete_tasks.grid(row=2, column=1)

        self._in_progress_header.grid(row=0, column=2)
        self._in_progress_non_concrete_tasks.grid(row=1, column=2)
        self._in_progress_concrete_tasks.grid(row=2, column=2)

        self._completed_header.grid(row=0, column=3)
        self._completed_non_concrete_tasks.grid(row=1, column=3)
        self._completed_concrete_tasks.grid(row=2, column=3)

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: self._update_tasks())

        self._update_tasks()

    def _update_tasks(self) -> None:
        task_groups = self._logic_layer.get_tasks_grouped_by_progress_and_concreteness()

        attributes_register = self._logic_layer.get_task_system().attributes_register()

        not_started_non_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.not_started_tasks.non_concrete_tasks
        )
        self._not_started_non_concrete_tasks.update_tasks(
            not_started_non_concrete_tasks
        )

        not_started_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.not_started_tasks.concrete_tasks
        )
        self._not_started_concrete_tasks.update_tasks(not_started_concrete_tasks)

        in_progress_non_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.in_progress_tasks.non_concrete_tasks
        )
        self._in_progress_non_concrete_tasks.update_tasks(
            in_progress_non_concrete_tasks
        )

        in_progress_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.in_progress_tasks.concrete_tasks
        )
        self._in_progress_concrete_tasks.update_tasks(in_progress_concrete_tasks)

        completed_non_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.completed_tasks.non_concrete_tasks
        )
        self._completed_non_concrete_tasks.update_tasks(completed_non_concrete_tasks)

        completed_concrete_tasks = (
            (uid, attributes_register[uid].name)
            for uid in task_groups.completed_tasks.concrete_tasks
        )
        self._completed_concrete_tasks.update_tasks(completed_concrete_tasks)
