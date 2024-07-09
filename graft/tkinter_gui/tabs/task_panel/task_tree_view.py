import functools
import tkinter as tk
from tkinter import ttk
from typing import Self

from graft import architecture
from graft.domain import tasks
from graft.tkinter_gui import event_broker


class TaskTreeView(ttk.Treeview):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        def update_tree(_: event_broker.Event | None, self: Self) -> None:
            self.delete(*self.get_children())

            for (
                uid,
                attributes,
            ) in self._logic_layer.get_task_attributes_register_view().items():
                formatted_uid = str(uid)
                formatted_name = str(attributes.name)
                self.insert(
                    "",
                    tk.END,
                    values=[formatted_uid, formatted_name],
                )

        def publish_task_selected_event(_, self: Self) -> None:
            item_id = self.focus()

            if not item_id:
                return

            task = tasks.UID(int(self.item(item_id, "values")[0]))
            broker = event_broker.get_singleton()

            broker.publish(event_broker.TaskSelected(task))

        super().__init__(master, columns=("id", "name"), show="headings")
        self._logic_layer = logic_layer

        self.heading("id", text="ID")
        self.heading("name", text="Name")

        self.column("id", width=40)

        update_tree(None, self)

        self.bind(
            "<<TreeviewSelect>>",
            functools.partial(publish_task_selected_event, self=self),
        )

        broker = event_broker.get_singleton()
        broker.subscribe(
            event_broker.SystemModified, functools.partial(update_tree, self=self)
        )
