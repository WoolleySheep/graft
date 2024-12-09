import tkinter as tk
from collections.abc import Iterable
from tkinter import Event, EventType, ttk

from graft.domain import tasks
from graft.layers.presentation.tkinter_gui import event_broker


class TaskTreeView(ttk.Treeview):
    def __init__(
        self,
        master: tk.Misc,
        id_column_width_pixels: int,
        name_column_width_pixels: int,
        height_rows: int,
    ) -> None:
        super().__init__(
            master, columns=("id", "name"), show="headings", height=height_rows
        )

        self.heading("id", text="ID")
        self.heading("name", text="Name")

        self.column("id", width=id_column_width_pixels)
        self.column("name", width=name_column_width_pixels)

        self.bind("<<TreeviewSelect>>", self._on_row_selected)

    def _on_row_selected(self, event: Event) -> None:
        if event.type is not EventType.VirtualEvent:
            msg = "Event type must be VirtualEvent"
            raise ValueError(msg)

        if event.widget != self:
            pass

        selected_row_id = self.focus()
        selected_row_values = self.item(selected_row_id, "values")
        formatted_task = selected_row_values[0]  # Task ID in column 0
        task = tasks.UID(int(formatted_task))

        broker = event_broker.get_singleton()
        broker.publish(event_broker.TaskSelected(task))

    def update_tasks(self, task_group: Iterable[tuple[tasks.UID, tasks.Name]]) -> None:
        """Update the tasks displayed."""
        self.delete(*self.get_children())

        for (
            uid,
            name,
        ) in sorted(task_group, key=lambda x: x[0]):  # Task ID in column 0
            formatted_uid = str(uid)
            formatted_name = str(name)
            self.insert(
                "",
                tk.END,
                values=[formatted_uid, formatted_name],
            )
