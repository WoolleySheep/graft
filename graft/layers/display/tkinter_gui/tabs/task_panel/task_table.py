import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.layers.display.tkinter_gui.tabs.task_panel.task_tree_view import TaskTreeView


class TaskTable(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self._logic_layer = logic_layer

        self._task_tree_view = TaskTreeView(self, logic_layer=self._logic_layer)

        # Create a Scrollbar
        self._scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self._task_tree_view.yview
        )

        # Configure the Treeview to use the scrollbar
        self._task_tree_view.configure(yscrollcommand=self._scrollbar.set)

        self._task_tree_view.grid(row=0, column=0)
        self._scrollbar.grid(row=0, column=1, sticky="ns")
        # Place the scrollbar on the right side of the Treeview
