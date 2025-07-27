import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.domain import tasks
from graft.domain.priority_order import (
    get_active_concrete_tasks_in_descending_priority_order,
)
from graft.layers.presentation.tkinter_gui import event_broker
from graft.layers.presentation.tkinter_gui.helpers import (
    importance_display,
    progress_display,
)


class PriorityTreeView(ttk.Treeview):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(
            master,
            columns=("rank", "id", "name", "highest_importance", "progress"),
            show="headings",
        )
        self._logic_layer = logic_layer

        self.heading("rank", text="Rank")
        self.heading("id", text="ID")
        self.heading("name", text="Name")
        self.heading("highest_importance", text="Highest Importance")
        self.heading("progress", text="Progress")

        self.column("rank", width=40)
        self.column("id", width=40)
        self.column("highest_importance", width=150)
        self.column("progress", width=100)

        self._update_tasks()

        self.bind("<<TreeviewSelect>>", lambda _: self._publish_task_selected_event())

        broker = event_broker.get_singleton()
        broker.subscribe(event_broker.SystemModified, lambda _: self._update_tasks())

    def _publish_task_selected_event(self) -> None:
        item_id = self.focus()

        if not item_id:
            return

        task = tasks.UID(int(self.item(item_id, "values")[1]))
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task))

    def _update_tasks(self) -> None:
        self.delete(*self.get_children())

        for rank, (uid, importance, _, _) in enumerate(
            get_active_concrete_tasks_in_descending_priority_order(
                self._logic_layer.get_system()
            ),
            start=1,
        ):
            name = self._logic_layer.get_task_system().attributes_register()[uid].name
            progress = self._logic_layer.get_task_system().get_progress(uid)
            formatted_rank = str(rank)
            formatted_uid = str(uid)
            formatted_name = str(name)
            formatted_importance = (
                importance_display.format(importance) if importance is not None else ""
            )
            formatted_progress = progress_display.format(progress)
            self.insert(
                "",
                tk.END,
                values=[
                    formatted_rank,
                    formatted_uid,
                    formatted_name,
                    formatted_importance,
                    formatted_progress,
                ],
            )
