import tkinter as tk
from collections.abc import Iterable
from tkinter import ttk

from graft.domain import tasks
from graft.tkinter_gui import event_broker


class TaskTreeView(ttk.Treeview):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, columns=("id", "name"), show="headings")

        self.heading("id", text="ID")
        self.heading("name", text="Name")

        self.column("id", width=40)

        self.bind("<<TreeviewSelect>>", lambda _: self._publish_selected_task_event())

    def _publish_selected_task_event(self) -> None:
        item_id = self.focus()

        if not item_id:
            return

        task = tasks.UID(int(self.item(item_id, "values")[0]))
        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task))

    def update_tasks(self, task_group: Iterable[tuple[tasks.UID, tasks.Name]]) -> None:
        """Update the tasks displayed."""
        self.delete(*self.get_children())

        for (
            uid,
            name,
        ) in sorted(task_group, key=lambda x: x[0]):
            formatted_uid = str(uid)
            formatted_name = str(name)
            self.insert(
                "",
                tk.END,
                values=[formatted_uid, formatted_name],
            )
