import functools
import tkinter as tk
from tkinter import ttk
from typing import Self

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker


class PriorityTreeView(ttk.Treeview):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def update_tree(_: event_broker.Event | None, self: Self) -> None:
            self.delete(*self.get_children())

            for rank, uid in enumerate(
                self._logic_layer.get_active_concrete_tasks_in_priority_order(), start=1
            ):
                name = self._logic_layer.get_task_attributes_register_view()[uid].name
                progress = self._logic_layer.get_task_system_view().get_progress(uid)
                formatted_rank = str(rank)
                formatted_uid = str(uid)
                formatted_name = str(name) if name is not None else ""
                formatted_progress = progress.value
                self.insert(
                    "",
                    tk.END,
                    values=[
                        formatted_rank,
                        formatted_uid,
                        formatted_name,
                        formatted_progress,
                    ],
                )

        def publish_task_selected_event(_, self: Self) -> None:
            item_id = self.focus()

            if not item_id:
                return

            task = tasks.UID(int(self.item(item_id, "values")[1]))
            broker = event_broker.get_singleton()

            broker.publish(event_broker.TaskSelected(task))

        super().__init__(
            master, columns=("rank", "id", "name", "progress"), show="headings"
        )
        self._logic_layer = logic_layer

        self.heading("rank", text="Rank")
        self.heading("id", text="ID")
        self.heading("name", text="Name")
        self.heading("progress", text="Progress")

        self.column("rank", width=40)
        self.column("id", width=40)
        self.column("progress", width=100)

        update_tree(None, self)

        self.bind(
            "<<TreeviewSelect>>",
            functools.partial(publish_task_selected_event, self=self),
        )

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.SystemModified, functools.partial(update_tree, self=self)
        )
