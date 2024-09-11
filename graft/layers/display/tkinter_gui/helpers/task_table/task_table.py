import tkinter as tk
from collections.abc import Iterable
from tkinter import ttk

from graft.domain import tasks
from graft.layers.display.tkinter_gui.helpers.task_table.task_tree_view import (
    TaskTreeView,
)


class TaskTable(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        id_column_width_pixels: int,
        name_column_width_pixels: int,
        height_rows: int,
    ) -> None:
        super().__init__(master)
        self._task_tree_view = TaskTreeView(
            self,
            id_column_width_pixels=id_column_width_pixels,
            name_column_width_pixels=name_column_width_pixels,
            height_rows=height_rows,
        )

        # Create a Scrollbar
        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._task_tree_view.yview
        )

        # Configure the Treeview to use the scrollbar
        self._task_tree_view.configure(yscrollcommand=self._scrollbar.set)

        self._task_tree_view.grid(row=0, column=0)
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        # Place the scrollbar on the right side of the Treeview

    def update_tasks(self, task_group: Iterable[tuple[tasks.UID, tasks.Name]]) -> None:
        """Update the tasks displayed."""
        self._task_tree_view.update_tasks(task_group)
