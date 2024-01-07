import tkinter as tk
from tkinter import ttk

from graft import architecture
from graft.tkinter_gui.hierarchy_panel.task_tree_view import TaskTreeView


class TaskLegendTable(tk.Frame):
    def __init__(self, master: tk.Misc, logic_layer: architecture.LogicLayer) -> None:
        super().__init__(master)
        self.logic_layer = logic_layer

        self.tree_view = TaskTreeView(self, logic_layer)

        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.tree_view.yview
        )

        self.tree_view.configure(yscrollcommand=self.scrollbar.set)

        self.tree_view.grid(row=0, column=0)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
